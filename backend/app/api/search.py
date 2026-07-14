from fastapi import APIRouter, HTTPException

from app.services import get_rag_service
from app.schemas.search import SearchRequest, SearchResponse

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search(request: SearchRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    rag = get_rag_service()
    if rag is None:
        raise HTTPException(status_code=503, detail="检索服务暂不可用，请稍后重试")

    result = rag.answer(request.question)
    return SearchResponse(answer=result["answer"], sources=result.get("sources", []))