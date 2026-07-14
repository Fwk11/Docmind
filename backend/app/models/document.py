"""
文档数据模型
============
对应数据库中的 documents 表，存储上传文档的基本信息。

每上传一个文档，就会在这张表里插入一条记录：
- id: 自增主键，唯一标识一个文档
- file_name: 文件名（如 "技术规范.pdf"）
- file_type: 文件类型（如 "pdf"、"docx"、"md"）
- file_path: 文件在服务器上的存储路径
- upload_time: 上传时间

类比：这张表就像图书馆的图书目录卡片，记录了每本书的基本信息。
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Document(Base):
    """文档模型：映射到 documents 表"""
    __tablename__ = "documents"

    # 主键：自增 ID，每个文档的唯一标识
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 文件名：如 "技术规范.pdf"，最长 255 字符
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # 文件类型：如 "pdf"、"docx"、"md"，最长 50 字符
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # 文件存储路径：服务器上的绝对路径，最长 500 字符
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    # 上传时间：默认使用当前 UTC 时间
    upload_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )