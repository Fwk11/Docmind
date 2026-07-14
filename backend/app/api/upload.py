"""
文档上传 API — 项目最核心的接口！

上传文档后自动完成：校验→保存→记录→解析→分块→向量化→存向量→记录分块
只有完成所有步骤，文档才能被AI检索和回答问题
"""
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

# 上传文件保存目录：backend/app/uploads/
UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".md", ".markdown"}
# 最大文件大小：100MB
MAX_FILE_SIZE = 100 * 1024 * 1024

# 文本分块服务（全局单例）
SPLITTER_SERVICE = SplitterService()


def _sanitize_filename(filename: str) -> str:
    """清理文件名防路径穿越攻击，只保留字母数字下划线连字符点号"""
    name = Path(filename).name
    name = re.sub(r"[^\w\-.]", "_", name)
    return name


def _allowed_file(filename: str) -> bool:
    """检查文件扩展名是否在允许列表中"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def _save_upload_file(upload_file: UploadFile, destination: Path) -> None:
    """流式保存文件，每次读1MB，边读边检查大小，避免内存溢出"""
    total_size = 0
    with destination.open("wb") as buffer:
        while True:
            chunk = upload_file.file.read(1024 * 1024)  # 每次读1MB
            if not chunk:
                break
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE:  # 超过100MB立即停止
                destination.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="文件大小超过 100MB 限制",
                )
            buffer.write(chunk)


def _load_document_content(file_path: Path) -> List[Dict[str, Any]]:
    """根据文件类型选解析器：PDF用PyMuPDF，DOCX用python-docx，MD用正则清洗"""
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
    """上传文档：校验→保存→记录→解析→分块→向量化→存向量→记录分块"""
    # 校验文件名和类型
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    if not _allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="仅支持 PDF、DOCX、Markdown 文件")

    # 清理文件名 + 处理重名(自动加后缀)
    safe_name = _sanitize_filename(file.filename)
    destination = UPLOAD_DIR / safe_name
    counter = 1
    while destination.exists():
        stem = Path(safe_name).stem
        suffix = Path(safe_name).suffix
        safe_name = f"{stem}_{counter}{suffix}"
        destination = UPLOAD_DIR / safe_name
        counter += 1

    # 保存文件到磁盘
    try:
        _save_upload_file(file, destination)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(exc)}") from exc

    # 在数据库中记录文档信息
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

    # 解析文档内容
    parsed_items = _load_document_content(destination)
    if not parsed_items:
        return {"success": True, "document_id": document.id, "filename": safe_name}

    # 文本分块
    chunks = SPLITTER_SERVICE.split(parsed_items)
    if not chunks:
        return {"success": True, "document_id": document.id, "filename": safe_name}

    # 向量化 + 存入 ChromaDB
    embedding_service = get_embedding_service()
    vector_store = get_vector_store()

    if embedding_service and vector_store:
        # 将每个文本块转换为向量
        try:
            embedded_chunks = embedding_service.embed_chunks(chunks)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"向量生成失败: {exc}") from exc

        # 将向量 + 原文 + 元数据存入 ChromaDB
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

    # 在数据库中记录分块信息
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