"""
历史记录响应模型
================
定义聊天历史列表 API 的返回格式。

每条历史记录包含：问题、回答、创建时间
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HistoryItem(BaseModel):
    """历史记录项模型"""
    model_config = ConfigDict(from_attributes=True)

    id: int                   # 记录 ID
    question: str             # 用户的问题
    answer: str               # AI 的回答
    create_time: datetime     # 对话发生的时间