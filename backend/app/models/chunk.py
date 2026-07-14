# 这是文档分块数据模型，映射到 DocumentChunk 表。
import json
from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class DocumentChunk(Base):
    """保存文档切分后的文本块。"""
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=True)

    def set_metadata(self, metadata: dict) -> None:
        """将字典类型的元数据序列化为 JSON 存储。"""
        self.chunk_metadata = json.loads(json.dumps(metadata)) if metadata is not None else None
