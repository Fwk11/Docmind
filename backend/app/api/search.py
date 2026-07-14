"""
知识检索 API 接口
==================
提供基于文档的知识检索功能，返回 AI 回答和参考来源。

和聊天接口的区别：
- 聊天：只返回 AI 的回答
- 检索：返回 AI 的回答 + 参考来源（告诉用户答案从哪来的）

参考来源包括：
- 文档片段的原文
- 元数据（文件名、页码等）
- 语义距离（和问题的相关程度）
"""

from fastapi import APIRouter, HTTPException

from app.services import get_rag_service
from app.schemas.search import SearchRequest, SearchResponse

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search(request: SearchRequest):
    """
    知识检索接口

    流程：
    1. 校验问题不为空
    2. 调用 RAG 服务获取回答和参考来源
    3. 返回回答 + 参考来源列表
    """
    # 校验：问题不能为空
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    # 获取 RAG 服务实例
    rag = get_rag_service()
    if rag is None:
        raise HTTPException(status_code=503, detail="检索服务暂不可用，请稍后重试")

    # 调用 RAG 服务获取回答和来源
    result = rag.answer(request.question)
    return SearchResponse(answer=result["answer"], sources=result.get("sources", []))