"""
普通聊天 API 接口
==================
提供非流式的聊天功能：用户提问，等 AI 完整回答后一次性返回。

和 chat_stream.py 的区别：
- 本接口：AI 说完所有话后，一次性返回完整回答
- 流式接口：AI 边说边返回，前端逐字显示（打字机效果）

本接口适合不需要实时显示的场景，比如后台批量处理。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.models.chat_history import ChatHistory
from app.services import get_rag_service
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db_session)):
    """
    普通聊天接口：等 AI 说完再返回

    流程：
    1. 校验问题不为空
    2. 调用 RAG 服务获取 AI 回答
    3. 保存聊天记录到数据库
    4. 返回回答和历史记录 ID
    """
    # 校验：问题不能为空
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    # 获取 RAG 服务实例
    rag = get_rag_service()
    if rag is None:
        raise HTTPException(status_code=503, detail="检索服务暂不可用，请稍后重试")

    # 调用 RAG 服务获取回答（包含检索+生成）
    result = rag.answer(request.question)
    answer = result.get("answer", "")

    # 保存聊天记录到数据库
    try:
        history = ChatHistory(question=request.question, answer=answer)
        db.add(history)
        db.commit()
        db.refresh(history)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存聊天历史失败: {exc}") from exc

    return ChatResponse(answer=answer, history_id=history.id)