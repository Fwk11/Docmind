# 这是 Markdown 文档加载服务模块，负责读取 Markdown 文件并清洗标签。
import re
from pathlib import Path
from typing import Dict, List, Union


class MarkdownLoaderService:
    """用于读取 Markdown 文件并移除格式标签，生成统一的 Document 对象列表。"""

    def __init__(self, markdown_path: Union[str, Path]):
        """初始化时传入 Markdown 文件路径。"""
        self.markdown_path = Path(markdown_path)

    @staticmethod
    def _clean_markdown(text: str) -> str:
        """移除常见 Markdown 标签，保留纯文本内容。"""
        # 删除代码块
        text = re.sub(r"```[\s\S]*?```", "", text)
        # 删除行内代码
        text = re.sub(r"`([^`]*)`", r"\1", text)
        # 删除图片语法
        text = re.sub(r"!\[[^\]]*\]\([^\)]*\)", "", text)
        # 删除链接语法，保留链接文字
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        # 删除标题符号
        text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
        # 删除列表符号
        text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
        # 删除引用符号
        text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
        # 删除强调符号
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*((?!\*).+?)\*", r"\1", text)
        text = re.sub(r"__([^_]+)__", r"\1", text)
        text = re.sub(r"_([^_]+)_", r"\1", text)
        # 删除 HTML 标签
        text = re.sub(r"<[^>]+>", "", text)
        # 合并多余空白
        text = re.sub(r"\n{2,}", "\n\n", text)
        return text.strip()

    def load(self) -> List[Dict[str, Union[str, int]]]:
        """读取 Markdown 文件并输出清洗后的文本段落。"""
        if not self.markdown_path.exists():
            raise FileNotFoundError(f"Markdown 文件不存在: {self.markdown_path}")
        if not self.markdown_path.is_file():
            raise ValueError(f"Markdown 路径不是文件: {self.markdown_path}")

        try:
            raw_text = self.markdown_path.read_text(encoding="utf-8")
        except Exception as exc:
            raise RuntimeError(f"读取 Markdown 文件失败: {self.markdown_path}") from exc

        cleaned_text = self._clean_markdown(raw_text)
        if not cleaned_text:
            return []

        try:
            paragraphs = [line.strip() for line in cleaned_text.splitlines() if line.strip()]
            results: List[Dict[str, Union[str, int]]] = []
            for index, paragraph in enumerate(paragraphs, start=1):
                results.append(
                    {
                        "text": paragraph,
                        "paragraph": index,
                        "source": self.markdown_path.name,
                    }
                )
            return results
        except Exception as exc:
            raise RuntimeError(f"解析 Markdown 内容失败: {self.markdown_path}") from exc
