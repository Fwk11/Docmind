"""
RAG 服务模块 — 项目的核心大脑！

什么是 RAG（Retrieval-Augmented Generation，检索增强生成）？
- 让 AI 基于你的文档回答问题，而不是凭空编造
- 流程：用户提问 → 检索相关文档 → 把文档塞给AI → AI基于文档回答

为什么需要 RAG？
- 大模型的知识有截止日期，不知道你的私有文档内容
- 直接问大模型，它可能瞎编（幻觉问题）
- RAG 让大模型"开卷考试"，基于真实文档回答，更准确

RAG 工作流程：
1. 用户提问："Python怎么定义函数？"
2. 向量化问题：把问题转成数字向量
3. 向量检索：在 ChromaDB 中找最相似的5个文本块
4. 构造提示词：把找到的文本块作为上下文，和问题一起给大模型
5. 大模型生成回答：基于上下文回答问题

本模块提供两种回答方式：
- answer()：一次性返回完整回答
- answer_stream()：流式返回，打字机效果
"""
from typing import Any, Dict, Generator, List

from app.services.embedding import EmbeddingService
from app.services.llm import LLMService
from app.services.vector_store import VectorStore


class RAGService:
    """RAG 核心服务：检索增强生成"""

    def __init__(self, vector_store: VectorStore, llm_service: LLMService, embedding_service: EmbeddingService):
        """依赖注入三个服务：向量数据库 + 大模型 + 向量化"""
        self.vector_store = vector_store
        self.llm_service = llm_service
        self.embedding_service = embedding_service

    def answer(self, question: str) -> Dict[str, Any]:
        """一次性回答：问题→向量化→检索→构造提示词→大模型生成"""
        if not question:
            raise ValueError("问题不能为空")

        # 第1步：把问题向量化
        query_embedding = self.embedding_service.embed_query(question)
        # 第2步：在向量数据库中检索最相似的5个文本块
        top_chunks = self.vector_store.query_top_k(query_embedding, top_k=5)

        # 第3步：构造提示词（把检索到的内容作为上下文）
        context = "\n\n".join([f"来源段落：{chunk['text']}" for chunk in top_chunks])
        prompt = (
            f"请基于以下内容回答问题，并给出引用来源。\n\n{context}\n\n问题：{question}\n\n回答："
        )

        # 第4步：调用大模型生成回答
        answer = self.llm_service.generate(prompt)

        # 返回回答 + 来源信息
        sources = [chunk["metadata"] for chunk in top_chunks]
        return {
            "answer": answer,
            "sources": sources,
        }

    def answer_stream(self, question: str) -> Generator[str, None, None]:
        """流式回答：和answer()流程一样，但用流式生成实现打字机效果"""
        if not question:
            raise ValueError("问题不能为空")

        # 向量化问题 → 检索相关文档
        query_embedding = self.embedding_service.embed_query(question)
        top_chunks = self.vector_store.query_top_k(query_embedding, top_k=5)

        # 构造提示词
        context = "\n\n".join([f"来源段落：{chunk['text']}" for chunk in top_chunks])
        prompt = (
            f"请基于以下内容回答问题，并给出引用来源。\n\n{context}\n\n问题：{question}\n\n回答："
        )

        # 流式生成，每个字yield一次
        yield from self.llm_service.generate_stream(prompt)