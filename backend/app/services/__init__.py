"""
服务工厂模块 — 统一创建和管理所有服务实例

为什么用工厂模式？
- 服务之间有依赖：RAGService 需要 VectorStore + LLMService + EmbeddingService
- 如果每个API都自己创建服务，会重复初始化浪费资源
- 用全局变量+懒加载，第一次使用时创建，之后复用

初始化顺序：VectorStore → EmbeddingService → LLMService → RAGService
"""
from pathlib import Path

# ChromaDB 数据持久化目录：backend/chromadb/
CHROMA_DIR = Path(__file__).resolve().parents[2] / "chromadb"
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# 全局服务实例（单例），None 表示尚未初始化
_vector_store = None
_embedding_service = None
_llm_service = None
_rag_service = None


def get_vector_store():
    """获取向量存储服务实例（懒加载单例）"""
    global _vector_store
    if _vector_store is None:
        try:
            from app.services.vector_store import VectorStore
            _vector_store = VectorStore(persist_directory=str(CHROMA_DIR))
        except Exception:
            pass  # 初始化失败返回None，调用方需处理
    return _vector_store


def get_embedding_service():
    """获取向量化服务实例（懒加载单例）"""
    global _embedding_service
    if _embedding_service is None:
        try:
            from app.services.embedding import EmbeddingService
            _embedding_service = EmbeddingService()
        except Exception:
            pass
    return _embedding_service


def get_llm_service():
    """获取大模型服务实例（懒加载单例）"""
    global _llm_service
    if _llm_service is None:
        try:
            from app.services.llm import LLMService
            _llm_service = LLMService()
        except Exception:
            pass
    return _llm_service


def get_rag_service():
    """获取RAG服务实例（懒加载单例），依赖其他三个服务都初始化成功"""
    global _rag_service
    if _rag_service is None:
        vs = get_vector_store()   # 向量数据库
        llm = get_llm_service()   # 大模型
        emb = get_embedding_service()  # 向量化
        if vs and llm and emb:  # 三个依赖都成功才创建RAG服务
            from app.services.rag_service import RAGService
            _rag_service = RAGService(vs, llm, emb)
    return _rag_service