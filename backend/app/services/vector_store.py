"""
向量存储服务模块 — 封装 ChromaDB 向量数据库操作

什么是向量数据库？
- 专门存储和检索向量的数据库
- 普通数据库按关键词搜索，向量数据库按语义相似度搜索
- 例如搜"如何学习Python"，能找到"Python入门教程"，即使没有关键词匹配

为什么用 ChromaDB？
- 开源轻量，适合小型项目
- 支持本地持久化（数据保存在磁盘上，重启不丢失）
- 内置向量相似度搜索，不需要自己实现
- PersistentClient 模式下数据保存在指定目录

核心操作：
1. add_documents — 添加文档向量（上传时用）
2. query_top_k — 搜索最相似的k个文档（问答时用）
3. delete_documents — 删除指定向量（删文档时用）
"""
from typing import Any, Dict, List

import chromadb


class VectorStore:
    """向量存储服务：封装 ChromaDB 的增删查操作"""

    def __init__(self, persist_directory: str = None):
        """初始化 ChromaDB 客户端和集合（类似数据库的表）"""
        try:
            # PersistentClient：数据持久化到磁盘
            self.client = chromadb.PersistentClient(path=persist_directory)
            # get_or_create_collection：获取或创建名为 docmind_collection 的集合
            self.collection = self.client.get_or_create_collection(name="docmind_collection")
        except Exception as exc:
            raise RuntimeError(f"初始化向量存储失败: {exc}") from exc

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """添加文档向量到 ChromaDB（上传文档时调用）"""
        try:
            ids = [str(doc["id"]) for doc in documents]           # 唯一标识
            embeddings = [doc["embedding"] for doc in documents]  # 向量
            metadatas = [doc.get("metadata", {}) for doc in documents]  # 元数据
            documents_text = [doc.get("text", "") for doc in documents]  # 原文
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents_text,
            )
        except Exception as exc:
            raise RuntimeError(f"向量存储新增文档失败: {exc}") from exc

    def delete_documents(self, ids: List[str]) -> None:
        """根据ID删除向量（删除文档时调用）"""
        try:
            self.collection.delete(ids=ids)
        except Exception as exc:
            raise RuntimeError(f"删除向量文档失败: {exc}") from exc

    def query_top_k(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        搜索最相似的 top_k 个文本块（问答时调用）

        原理：用问题的向量在数据库中找余弦距离最近的k个向量
        距离越小 = 语义越相似 = 越相关
        """
        try:
            results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
            matches = []
            for idx in range(len(results["ids"][0])):
                matches.append(
                    {
                        "id": results["ids"][0][idx],
                        "text": results["documents"][0][idx],
                        "metadata": results["metadatas"][0][idx],
                        "distance": results["distances"][0][idx],
                    }
                )
            return matches
        except Exception as exc:
            raise RuntimeError(f"向量查询失败: {exc}") from exc