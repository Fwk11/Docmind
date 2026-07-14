from typing import Any, Dict, List

import chromadb


class VectorStore:

    def __init__(self, persist_directory: str = None):
        try:
            self.client = chromadb.PersistentClient(path=persist_directory)
            self.collection = self.client.get_or_create_collection(name="docmind_collection")
        except Exception as exc:
            raise RuntimeError(f"初始化向量存储失败: {exc}") from exc

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        try:
            ids = [str(doc["id"]) for doc in documents]
            embeddings = [doc["embedding"] for doc in documents]
            metadatas = [doc.get("metadata", {}) for doc in documents]
            documents_text = [doc.get("text", "") for doc in documents]
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents_text,
            )
        except Exception as exc:
            raise RuntimeError(f"向量存储新增文档失败: {exc}") from exc

    def delete_documents(self, ids: List[str]) -> None:
        try:
            self.collection.delete(ids=ids)
        except Exception as exc:
            raise RuntimeError(f"删除向量文档失败: {exc}") from exc

    def query_top_k(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
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