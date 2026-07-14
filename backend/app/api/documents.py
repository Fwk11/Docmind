"""
文档管理 API — 提供列表查询、详情查询和删除功能

删除文档时同时清理：服务器文件 + 数据库记录 + ChromaDB向量数据
"""
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.schemas.document import DocumentDetailResponse, DocumentListItem
from app.services import get_vector_store

router = APIRouter()


@router.get("/documents", response_model=List[DocumentListItem])
def list_documents(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    db: Session = Depends(get_db_session),
):
    """获取文档列表，按上传时间倒序，支持分页"""
    documents = db.query(Document).order_by(Document.upload_time.desc()).offset(skip).limit(limit).all()
    return documents


@router.get("/documents/{document_id}", response_model=DocumentDetailResponse)
def get_document(document_id: int, db: Session = Depends(get_db_session)):
    """获取文档详情，包含该文档的所有分块内容"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="文档未找到")

    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
        .all()
    )

    return DocumentDetailResponse(
        id=document.id,
        file_name=document.file_name,
        file_type=document.file_type,
        upload_time=document.upload_time,
        chunks=chunks,
    )


@router.delete("/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db_session)):
    """删除文档：清理服务器文件+数据库记录+ChromaDB向量数据"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="文档未找到")

    # 1. 删除服务器上的文件
    file_path = Path(document.file_path)
    if file_path.exists():
        file_path.unlink()

    # 2. 删除数据库中的分块记录
    db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()

    # 3. 删除 ChromaDB 中的向量数据
    vector_store = get_vector_store()
    if vector_store:
        try:
            all_ids = vector_store.collection.get(where={"document_id": document_id})
            if all_ids and all_ids["ids"]:
                vector_store.delete_documents(all_ids["ids"])
        except Exception:
            pass  # 向量删除失败不影响整体删除

    # 删除文档记录
    db.delete(document)
    db.commit()
    return {"success": True, "message": "文档已删除"}