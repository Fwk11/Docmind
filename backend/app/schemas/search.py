from typing import Any, Dict, List

from pydantic import BaseModel


class SearchRequest(BaseModel):
    question: str


class SearchSource(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any]
    distance: float


class SearchResponse(BaseModel):
    answer: str
    sources: List[SearchSource]