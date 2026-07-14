# 这是 DOCX 文档加载服务模块，负责按段落读取 Word 文档内容。
from pathlib import Path
from typing import Dict, List, Union

from docx import Document as DocxDocument


class DOCXLoaderService:
    """用于读取 DOCX 文件并将每个段落转换为统一 Document 对象列表。"""

    def __init__(self, docx_path: Union[str, Path]):
        """初始化时传入 DOCX 文件路径。"""
        self.docx_path = Path(docx_path)

    def load(self) -> List[Dict[str, Union[str, int]]]:
        """读取 DOCX 文件并返回段落文本列表。"""
        if not self.docx_path.exists():
            raise FileNotFoundError(f"DOCX 文件不存在: {self.docx_path}")
        if not self.docx_path.is_file():
            raise ValueError(f"DOCX 路径不是文件: {self.docx_path}")

        try:
            document = DocxDocument(self.docx_path)
        except Exception as exc:
            raise RuntimeError(f"打开 DOCX 文件失败: {self.docx_path}") from exc

        results: List[Dict[str, Union[str, int]]] = []
        try:
            for index, paragraph in enumerate(document.paragraphs, start=1):
                text = paragraph.text.strip()
                if not text:
                    continue
                results.append(
                    {
                        "text": text,
                        "paragraph": index,
                        "source": self.docx_path.name,
                    }
                )
            return results
        except Exception as exc:
            raise RuntimeError(f"解析 DOCX 内容失败: {self.docx_path}") from exc
