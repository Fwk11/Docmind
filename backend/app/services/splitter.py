# 这是文本切分模块，采用简单的滑动窗口逻辑将文本拆分成块。
from typing import Any, Dict, List


class SplitterService:
    """将文本段落切分为固定大小的块，并保留原始元数据。"""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        """初始化切分器参数。"""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _split_text(self, text: str) -> List[str]:
        """将单段文本拆分为多个块，支持重叠。"""
        text = text.strip()
        if not text:
            return []

        chunks: List[str] = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk = text[start:end]

            if end < text_length:
                last_space = chunk.rfind(" ")
                if last_space > max(self.chunk_size // 2, 20):
                    end = start + last_space
                    chunk = text[start:end]

            chunk = chunk.strip()
            if chunk:
                chunks.append(chunk)

            if end >= text_length:
                break

            start = max(end - self.chunk_overlap, end)

        return chunks

    def split(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """将 Document 对象列表拆分成 Chunk 列表，并保留 metadata。"""
        chunks: List[Dict[str, Any]] = []
        for item in documents:
            text = item.get("text", "")
            if not text:
                continue

            metadata = {k: v for k, v in item.items() if k != "text"}
            try:
                texts = self._split_text(text)
            except Exception as exc:
                raise RuntimeError(f"文本切分失败: {exc}") from exc

            for index, chunk_text in enumerate(texts, start=1):
                chunks.append(
                    {
                        "text": chunk_text,
                        "metadata": {
                            **metadata,
                            "chunk_index": index,
                        },
                    }
                )
        return chunks
