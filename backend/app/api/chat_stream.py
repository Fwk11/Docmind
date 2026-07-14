"""
流式聊天 API 接口
==================
提供流式聊天功能：AI 边生成边返回，前端逐字显示（打字机效果）。

什么是 SSE（Server-Sent Events）？
- 一种服务器向浏览器推送数据的技术
- 服务器可以持续发送数据，浏览器实时接收
- 格式：每条消息以 "data: " 开头，以两个换行符结尾
- 和 WebSocket 的区别：SSE 是单向的（服务器→浏览器），WebSocket 是双向的

为什么聊天用 SSE 而不是普通 HTTP？
- AI 生成回答需要时间，如果等全部生成完再返回，用户要等很久
- SSE 让 AI 生成一个字就发一个字，用户马上能看到回答
- 体验就像 ChatGPT 那样，一个字一个字蹦出来
"""

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
    """
    流式聊天接口：AI 边生成边返回

    返回的是 StreamingResponse，不是普通 JSON 响应。
    StreamingResponse 会持续发送数据，直到生成器函数执行完毕。

    流程：
    1. 校验问题不为空
    2. 创建一个生成器函数（event_generator）
    3. 返回 StreamingResponse，把生成器作为内容源
    4. 生成器每次 yield 一条 SSE 消息
    5. AI 生成完毕后，保存完整回答到数据库
    """
    # 校验：问题不能为空
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    # 获取 RAG 服务实例
    rag = get_rag_service()
    if rag is None:
        raise HTTPException(status_code=503, detail="检索服务暂不可用，请稍后重试")

    def event_generator():
        """
        SSE 事件生成器

        这是一个生成器函数，每次 yield 一条 SSE 格式的消息。
        FastAPI 会把 yield 的内容逐条发送给浏览器。

        SSE 消息格式：
        data: {"content": "你"}\n\n
        data: {"content": "好"}\n\n
        data: [DONE]\n\n
        """
        full_answer = ""  # 累积完整回答

        try:
            # 调用 RAG 服务的流式生成方法
            for chunk in rag.answer_stream(request.question):
                full_answer += chunk  # 累积每个字
                # 构造 SSE 消息：data: JSON内容\n\n
                data = json.dumps({"content": chunk}, ensure_ascii=False)
                yield f"data: {data}\n\n"
        except Exception as exc:
            # 生成出错时，发送错误消息
            logger.error("Stream error: %s", exc)
            data = json.dumps({"error": str(exc)}, ensure_ascii=False)
            yield f"data: {data}\n\n"

        # 发送结束标记
        yield "data: [DONE]\n\n"

        # 流式生成完毕后，保存完整回答到数据库
        try:
            history = ChatHistory(question=request.question, answer=full_answer)
            db.add(history)
            db.commit()
        except Exception as exc:
            db.rollback()
            logger.error("Save history failed: %s", exc)

    # 返回流式响应
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",  # SSE 的 MIME 类型
        headers={
            "Cache-Control": "no-cache",       # 禁止缓存，确保实时性
            "Connection": "keep-alive",         # 保持连接
            "X-Accel-Buffering": "no",          # 禁止 Nginx 缓冲，确保即时传输
        },
    )