from typing import Any, Dict, List

from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5"):
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as exc:
            raise RuntimeError(f"加载 Embedding 模型失败: {model_name}") from exc

    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        texts = [chunk.get("text", "") for chunk in chunks]
        try:
            embeddings = self.model.encode(texts, show_progress_bar=False)
        except Exception as exc:
            raise RuntimeError("生成文本向量失败") from exc

        enriched: List[Dict[str, Any]] = []
        for chunk, vector in zip(chunks, embeddings):
            enriched.append(
                {
                    "text": chunk.get("text", ""),
                    "metadata": chunk.get("metadata", {}),
                    "embedding": vector.tolist() if hasattr(vector, "tolist") else vector,
                }
            )
        return enriched

    def embed_query(self, text: str) -> List[float]:
        try:
            vector = self.model.encode([text], show_progress_bar=False)[0]
            return vector.tolist() if hasattr(vector, "tolist") else vector
        except Exception as exc:
            raise RuntimeError("生成查询向量失败") from exc