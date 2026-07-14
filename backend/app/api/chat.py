from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.models.chat_history import ChatHistory
from app.services import get_rag_service
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db_session)):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    rag = get_rag_service()
    if rag is None:
        raise HTTPException(status_code=503, detail="检索服务暂不可用，请稍后重试")

    result = rag.answer(request.question)
    answer = result.get("answer", "")

    try:
        history = ChatHistory(question=request.question, answer=answer)
        db.add(history)
        db.commit()
        db.refresh(history)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存聊天历史失败: {exc}") from exc

    return ChatResponse(answer=answer, history_id=history.id)