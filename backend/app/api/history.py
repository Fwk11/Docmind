from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.models.chat_history import ChatHistory
from app.schemas.history import HistoryItem

router = APIRouter()


@router.get("/history", response_model=list[HistoryItem])
def list_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db_session),
):
    records = db.query(ChatHistory).order_by(ChatHistory.create_time.desc()).offset(skip).limit(limit).all()
    return records