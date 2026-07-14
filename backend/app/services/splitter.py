"""
文本分块模块 — 把长文本切成小块，方便向量化检索

为什么要分块？
- 向量模型有输入长度限制，太长的文本无法一次向量化
- 小块文本的向量更精确，检索效果更好
- 就像一本书分成章节，比整本书更容易找到需要的内容

滑动窗口分块原理：
- chunk_size=500：每块约500字
- chunk_overlap=100：相邻块重叠100字
- 重叠的作用：避免关键信息被切断在两块的边界处
  例如"机器学习是一种|人工智能技术"→ 如果切断在中间，检索时可能漏掉
  重叠后："机器学习是一种人工|人工智能技术"，两边都有完整语义
"""
from typing import Any, Dict, List


class SplitterService:
    """文本分块服务：滑动窗口切分，保留元数据"""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        """初始化分块参数：chunk_size每块字数，chunk_overlap重叠字数"""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _split_text(self, text: str) -> List[str]:
        """
        滑动窗口切分：每次取chunk_size字，下一块从end-overlap开始
        尽量在空格处断开，避免切断单词
        """
        text = text.strip()
        if not text:
            return []

        chunks: List[str] = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk = text[start:end]

            # 尝试在空格处断开，避免切断单词
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

            # 下一块从 end-overlap 开始，实现重叠
            start = max(end - self.chunk_overlap, end)

        return chunks

    def split(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """将文档列表拆分成块列表，保留原始元数据并添加 chunk_index"""
        chunks: List[Dict[str, Any]] = []
        for item in documents:
            text = item.get("text", "")
            if not text:
                continue

            # 提取元数据（除了text之外的所有字段）
            metadata = {k: v for k, v in item.items() if k != "text"}
            try:
                texts = self._split_text(text)
            except Exception as exc:
                raise RuntimeError(f"文本切分失败: {exc}") from exc

            # 为每个分块添加序号
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