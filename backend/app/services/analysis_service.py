# 这是 AI 分析服务模块，负责摘要、关键词、知识点和章节总结功能。
from typing import Dict, Any

from app.services.llm import LLMService
from app.services.prompt import (
    SUMMARY_PROMPT,
    KEYWORDS_PROMPT,
    KNOWLEDGE_POINTS_PROMPT,
    CHAPTER_SUMMARY_PROMPT,
)


class AnalysisService:
    """封装 AI 文本分析能力，使用统一 Prompt 生成不同类型结果。"""

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    def summarize(self, context: str) -> str:
        """生成文本摘要。"""
        if not context:
            raise ValueError("摘要内容不能为空")
        prompt = SUMMARY_PROMPT.format(context=context)
        return self.llm_service.generate(prompt)

    def keywords(self, context: str) -> str:
        """提取文本关键词。"""
        if not context:
            raise ValueError("关键词提取内容不能为空")
        prompt = KEYWORDS_PROMPT.format(context=context)
        return self.llm_service.generate(prompt)

    def knowledge_points(self, context: str) -> str:
        """提取文本知识点。"""
        if not context:
            raise ValueError("知识点提取内容不能为空")
        prompt = KNOWLEDGE_POINTS_PROMPT.format(context=context)
        return self.llm_service.generate(prompt)

    def chapter_summary(self, context: str) -> str:
        """生成章节总结。"""
        if not context:
            raise ValueError("章节总结内容不能为空")
        prompt = CHAPTER_SUMMARY_PROMPT.format(context=context)
        return self.llm_service.generate(prompt)
