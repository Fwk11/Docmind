"""
向量化服务模块 — 把文本转换成数字向量

什么是向量化（Embedding）？
- 把一段文字变成一组数字（向量），比如 [0.12, -0.34, 0.56, ...]
- 语义相近的文字，向量也相近（余弦相似度高）
- 这样就能通过数学计算找到"意思相近"的文本

为什么用 bge-small-zh-v1.5？
- BAAI（北京智源）开源的中文向量化模型
- small 版本体积小、速度快，适合个人电脑运行
- zh 表示中文优化，v1.5 是版本号
- 输出 512 维向量，足够表达中文语义

向量化在 RAG 中的作用：
1. 上传文档时：把每个文本块向量化，存入 ChromaDB
2. 用户提问时：把问题向量化，在 ChromaDB 中找最相似的文本块
3. 把找到的文本块作为上下文，喂给大模型生成回答
"""
from typing import Any, Dict, List

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """向量化服务：文本 → 数字向量"""

    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5"):
        """加载向量化模型，首次加载会从HuggingFace下载（约100MB）"""
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as exc:
            raise RuntimeError(f"加载 Embedding 模型失败: {model_name}") from exc

    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """批量向量化：把多个文本块转换成向量，用于上传文档时"""
        texts = [chunk.get("text", "") for chunk in chunks]
        try:
            embeddings = self.model.encode(texts, show_progress_bar=False)
        except Exception as exc:
            raise RuntimeError("生成文本向量失败") from exc

        # 把向量附加到原始数据上，返回 enriched 列表
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
        """单条向量化：把用户的问题转换成向量，用于检索时"""
        try:
            vector = self.model.encode([text], show_progress_bar=False)[0]
            return vector.tolist() if hasattr(vector, "tolist") else vector
        except Exception as exc:
            raise RuntimeError("生成查询向量失败") from exc