"""
聊天历史 API 接口
==================
提供查询聊天历史记录的接口，支持分页。

历史记录按时间倒序排列（最新的在前），
前端可以在"历史记录"页面查看之前的对话。
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db_session
from app.models.chat_history import ChatHistory
from app.schemas.history import HistoryItem

router = APIRouter()


@router.get("/history", response_model=list[HistoryItem])
def list_history(
    skip: int = Query(0, ge=0),       # 跳过前 N 条记录（用于翻页）
    limit: int = Query(50, ge=1, le=200),  # 返回最多 N 条记录
    db: Session = Depends(get_db_session),
):
    """
    获取聊天历史列表

    参数：
        skip: 跳过前几条（翻页偏移量）
        limit: 返回几条（每页数量）

    返回：
        按时间倒序排列的聊天记录列表
    """
    records = db.query(ChatHistory).order_by(ChatHistory.create_time.desc()).offset(skip).limit(limit).all()
    return records