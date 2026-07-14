import json
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.models.chat_history import ChatHistory
from app.services import get_rag_service
from app.schemas.chat import ChatRequest
from app.core.logging import get_logger

logger = get_logger("chat")
router = APIRouter()


@router.post("/chat/stream")
def chat_stream(request: ChatRequest, db: Session = Depends(get_db_session)):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    rag = get_rag_service()
    if rag is None:
        raise HTTPException(status_code=503, detail="检索服务暂不可用，请稍后重试")

    def event_generator():
        full_answer = ""
        try:
            for chunk in rag.answer_stream(request.question):
                full_answer += chunk
                data = json.dumps({"content": chunk}, ensure_ascii=False)
                yield f"data: {data}\n\n"
        except Exception as exc:
            logger.error("Stream error: %s", exc)
            data = json.dumps({"error": str(exc)}, ensure_ascii=False)
            yield f"data: {data}\n\n"

        yield "data: [DONE]\n\n"

        try:
            history = ChatHistory(question=request.question, answer=full_answer)
            db.add(history)
            db.commit()
        except Exception as exc:
            db.rollback()
            logger.error("Save history failed: %s", exc)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )