"""
文档分块数据模型
================
对应数据库中的 document_chunks 表，存储文档被切分后的文本块。

为什么需要分块？
- 一个文档可能有几百页，AI 一次处理不了那么长的文本
- 把文档切成小段（约 500 字一段），更容易精确匹配到相关内容
- 每个分块会被向量化后存入 ChromaDB，用于语义检索

类比：把一本书拆成一页一页的，每页就是一个 chunk。
"""

import json
from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class DocumentChunk(Base):
    """文档分块模型：映射到 document_chunks 表"""
    __tablename__ = "document_chunks"

    # 主键：自增 ID
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 外键：关联到 documents 表的 id，表示这个分块属于哪个文档
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False)
    # 分块文本内容：这个分块的原文
    content: Mapped[str] = mapped_column(String, nullable=False)
    # 分块序号：第几个分块（从 1 开始）
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    # 分块元数据：JSON 格式，存储页码、来源文件名等附加信息
    # 数据库列名是 "metadata"（SQLAlchemy 保留字，所以用 chunk_metadata 映射）
    chunk_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=True)

    def set_metadata(self, metadata: dict) -> None:
        """
        设置元数据

        为什么要做 JSON 序列化？
        因为 SQLAlchemy 的 JSON 列需要确保存入的是纯 JSON 兼容数据，
        通过 json.loads(json.dumps(...)) 可以去掉 Python 特有的对象（如 datetime），
        只保留基本类型（字符串、数字、列表、字典）。
        """
        self.chunk_metadata = json.loads(json.dumps(metadata)) if metadata is not None else None