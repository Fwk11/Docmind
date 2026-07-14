from typing import Any, Dict, Generator, List

from app.services.embedding import EmbeddingService
from app.services.llm import LLMService
from app.services.vector_store import VectorStore


class RAGService:

    def __init__(self, vector_store: VectorStore, llm_service: LLMService, embedding_service: EmbeddingService):
        self.vector_store = vector_store
        self.llm_service = llm_service
        self.embedding_service = embedding_service

    def answer(self, question: str) -> Dict[str, Any]:
        if not question:
            raise ValueError("问题不能为空")

        query_embedding = self.embedding_service.embed_query(question)
        top_chunks = self.vector_store.query_top_k(query_embedding, top_k=5)

        context = "\n\n".join([f"来源段落：{chunk['text']}" for chunk in top_chunks])
        prompt = (
            f"请基于以下内容回答问题，并给出引用来源。\n\n{context}\n\n问题：{question}\n\n回答："
        )

        answer = self.llm_service.generate(prompt)

        sources = [chunk["metadata"] for chunk in top_chunks]
        return {
            "answer": answer,
            "sources": sources,
        }

    def answer_stream(self, question: str) -> Generator[str, None, None]:
        if not question:
            raise ValueError("问题不能为空")

        query_embedding = self.embedding_service.embed_query(question)
        top_chunks = self.vector_store.query_top_k(query_embedding, top_k=5)

        context = "\n\n".join([f"来源段落：{chunk['text']}" for chunk in top_chunks])
        prompt = (
            f"请基于以下内容回答问题，并给出引用来源。\n\n{context}\n\n问题：{question}\n\n回答："
        )

        yield from self.llm_service.generate_stream(prompt)