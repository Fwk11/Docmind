"""
聊天历史数据模型
================
对应数据库中的 chat_histories 表，存储用户和 AI 的对话记录。

每次用户提问并得到 AI 回答后，问题和答案都会被保存下来。
这样用户可以在"历史记录"页面查看之前的对话。

类比：就像微信的聊天记录备份，随时可以翻看之前的对话。
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class ChatHistory(Base):
    """聊天历史模型：映射到 chat_histories 表"""
    __tablename__ = "chat_histories"

    # 主键：自增 ID
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 用户的问题
    question: Mapped[str] = mapped_column(String, nullable=False)
    # AI 的回答
    answer: Mapped[str] = mapped_column(String, nullable=False)
    # 创建时间：对话发生的时间
    create_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )