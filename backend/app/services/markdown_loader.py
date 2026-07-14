"""
Markdown 文档加载模块 — 读取 MD 文件并清洗格式标签

Markdown 有很多格式符号（#标题、**粗体**、[链接]等），
向量化时这些符号是噪音，需要清洗掉只保留纯文本。

清洗顺序很重要：先删代码块（避免误删内容），再删其他标签
"""
import re
from pathlib import Path
from typing import Dict, List, Union


class MarkdownLoaderService:
    """Markdown加载服务：清洗标签+提取纯文本"""

    def __init__(self, markdown_path: Union[str, Path]):
        """传入Markdown文件路径"""
        self.markdown_path = Path(markdown_path)

    @staticmethod
    def _clean_markdown(text: str) -> str:
        """清洗Markdown标签：代码块→行内代码→图片→链接→标题→列表→引用→强调→HTML→空白"""
        # 1. 删除代码块（必须先删，避免内容中的#等被误删）
        text = re.sub(r"```[\s\S]*?```", "", text)
        # 2. 行内代码：保留代码内容，去掉反引号
        text = re.sub(r"`([^`]*)`", r"\1", text)
        # 3. 图片：![alt](url) 整个删除
        text = re.sub(r"!\[[^\]]*\]\([^\)]*\)", "", text)
        # 4. 链接：[文字](url) 只保留文字
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        # 5. 标题符号：# ## ### 等
        text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
        # 6. 列表符号：- * + 和 1. 2. 等
        text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
        # 7. 引用符号：>
        text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
        # 8. 强调符号：**粗体** *斜体* __粗体__ _斜体_
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*((?!\*).+?)\*", r"\1", text)
        text = re.sub(r"__([^_]+)__", r"\1", text)
        text = re.sub(r"_([^_]+)_", r"\1", text)
        # 9. HTML标签
        text = re.sub(r"<[^>]+>", "", text)
        # 10. 合并多余空行
        text = re.sub(r"\n{2,}", "\n\n", text)
        return text.strip()

    def load(self) -> List[Dict[str, Union[str, int]]]:
        """读取Markdown文件并输出清洗后的文本段落"""
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