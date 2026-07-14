"""
知识检索相关的数据校验模型
==========================
定义检索 API 的请求和响应格式。

SearchRequest：前端发来的检索问题
SearchSource：检索到的参考来源（文档片段）
SearchResponse：AI 的回答 + 参考来源列表

参考来源是什么？
- AI 回答时，会从文档中找到最相关的几段话作为依据
- 这些依据就是"参考来源"，告诉用户答案从哪来的
- 这样用户可以验证 AI 的回答是否可靠
"""

from typing import Any, Dict, List

from pydantic import BaseModel


class SearchRequest(BaseModel):
    """检索请求模型：用户输入的问题"""
    question: str


class SearchSource(BaseModel):
    """检索来源模型：AI 回答所依据的文档片段"""
    id: str                       # 向量数据库中的 ID
    text: str                     # 文档片段的原文
    metadata: Dict[str, Any]      # 元数据（文件名、页码等）
    distance: float               # 与问题的语义距离，越小越相关


class SearchResponse(BaseModel):
    """检索响应模型：AI 的回答 + 参考来源"""
    answer: str                       # AI 生成的回答
    sources: List[SearchSource]       # 参考来源列表