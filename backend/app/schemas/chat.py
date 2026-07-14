"""
聊天相关的数据校验模型
======================
定义聊天 API 的请求和响应格式。

ChatRequest：前端发来的请求，包含用户的问题
ChatResponse：后端返回的响应，包含 AI 的回答和历史记录 ID
"""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """聊天请求模型：用户输入的问题"""
    question: str


class ChatResponse(BaseModel):
    """聊天响应模型：AI 的回答"""
    answer: str        # AI 生成的回答文本
    history_id: int    # 聊天记录在数据库中的 ID，方便后续追溯