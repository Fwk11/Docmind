from pathlib import Path

CHROMA_DIR = Path(__file__).resolve().parents[2] / "chromadb"
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

_vector_store = None
_embedding_service = None
_llm_service = None
_rag_service = None


def get_vector_store():
    global _vector_store
    if _vector_store is None:
        try:
            from app.services.vector_store import VectorStore
            _vector_store = VectorStore(persist_directory=str(CHROMA_DIR))
        except Exception:
            pass
    return _vector_store


def get_embedding_service():
    global _embedding_service
    if _embedding_service is None:
        try:
            from app.services.embedding import EmbeddingService
            _embedding_service = EmbeddingService()
        except Exception:
            pass
    return _embedding_service


def get_llm_service():
    global _llm_service
    if _llm_service is None:
        try:
            from app.services.llm import LLMService
            _llm_service = LLMService()
        except Exception:
            pass
    return _llm_service


def get_rag_service():
    global _rag_service
    if _rag_service is None:
        vs = get_vector_store()
        llm = get_llm_service()
        emb = get_embedding_service()
        if vs and llm and emb:
            from app.services.rag_service import RAGService
            _rag_service = RAGService(vs, llm, emb)
    return _rag_service