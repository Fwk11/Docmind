import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.services import get_embedding_service, get_vector_store
from app.services.docx_loader import DOCXLoaderService
from app.services.markdown_loader import MarkdownLoaderService
from app.services.pdf_loader import PDFLoaderService
from app.services.splitter import SplitterService

router = APIRouter()

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".md", ".markdown"}
MAX_FILE_SIZE = 100 * 1024 * 1024

SPLITTER_SERVICE = SplitterService()


def _sanitize_filename(filename: str) -> str:
    name = Path(filename).name
    name = re.sub(r"[^\w\-.]", "_", name)
    return name


def _allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def _save_upload_file(upload_file: UploadFile, destination: Path) -> None:
    total_size = 0
    with destination.open("wb") as buffer:
        while True:
            chunk = upload_file.file.read(1024 * 1024)
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:
                destination.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="文件大小超过 100MB 限制",
                )
            buffer.write(chunk)


def _load_document_content(file_path: Path) -> List[Dict[str, Any]]:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        loader = PDFLoaderService(file_path)
    elif suffix == ".docx":
        loader = DOCXLoaderService(file_path)
    elif suffix in {".md", ".markdown"}:
        loader = MarkdownLoaderService(file_path)
    else:
        raise HTTPException(status_code=400, detail="不支持的文件类型")

    try:
        return loader.load()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"文档解析失败: {exc}") from exc


@router.post("/upload", summary="上传文档文件")
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db_session)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    if not _allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="仅支持 PDF、DOCX、Markdown 文件")

    safe_name = _sanitize_filename(file.filename)
    destination = UPLOAD_DIR / safe_name
    counter = 1
    while destination.exists():
        stem = Path(safe_name).stem
        suffix = Path(safe_name).suffix
        safe_name = f"{stem}_{counter}{suffix}"
        destination = UPLOAD_DIR / safe_name
        counter += 1

    try:
        _save_upload_file(file, destination)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(exc)}") from exc

    try:
        document = Document(
            file_name=safe_name,
            file_type=Path(file.filename).suffix.lower().lstrip("."),
            file_path=str(destination),
            upload_time=datetime.now(timezone.utc),
        )
        db.add(document)
        db.commit()
        db.refresh(document)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"数据库写入失败: {str(exc)}") from exc

    parsed_items = _load_document_content(destination)
    if not parsed_items:
        return {"success": True, "document_id": document.id, "filename": safe_name}

    chunks = SPLITTER_SERVICE.split(parsed_items)
    if not chunks:
        return {"success": True, "document_id": document.id, "filename": safe_name}

    embedding_service = get_embedding_service()
    vector_store = get_vector_store()

    if embedding_service and vector_store:
        try:
            embedded_chunks = embedding_service.embed_chunks(chunks)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"向量生成失败: {exc}") from exc

        try:
            vector_store.add_documents(
                [
                    {
                        "id": f"{document.id}_{idx}",
                        "text": chunk["text"],
                        "metadata": {
                            "document_id": document.id,
                            "filename": safe_name,
                            **chunk.get("metadata", {}),
                        },
                        "embedding": chunk["embedding"],
                    }
                    for idx, chunk in enumerate(embedded_chunks, start=1)
                ]
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"向量存储失败: {exc}") from exc

    try:
        db.add_all(
            [
                DocumentChunk(
                    document_id=document.id,
                    content=chunk["text"],
                    chunk_index=int(chunk.get("metadata", {}).get("chunk_index", idx)),
                    chunk_metadata=chunk.get("metadata", {}),
                )
                for idx, chunk in enumerate(chunks, start=1)
            ]
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"文档分块写入失败: {exc}") from exc

    return {"success": True, "document_id": document.id, "filename": safe_name}