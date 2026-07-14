"""
DOCX 文档加载模块 — 按段落读取 Word 文档内容

使用 python-docx 库解析 .docx 文件：
- 按段落提取文本，每个非空段落作为一个文档段落
- 提取结果包含：文本内容、段落序号、来源文件名

为什么按段落提取？
- Word 文档天然按段落组织，保留段落结构
- 空段落跳过，只保留有内容的段落
"""
from pathlib import Path
from typing import Dict, List, Union

from docx import Document as DocxDocument


class DOCXLoaderService:
    """DOCX加载服务：按段落提取文本"""

    def __init__(self, docx_path: Union[str, Path]):
        """传入DOCX文件路径"""
        self.docx_path = Path(docx_path)

    def load(self) -> List[Dict[str, Union[str, int]]]:
        """读取DOCX并返回 [{text, paragraph, source}, ...] 列表，跳过空段落"""
        if not self.docx_path.exists():
            raise FileNotFoundError(f"DOCX 文件不存在: {self.docx_path}")
        if not self.docx_path.is_file():
            raise ValueError(f"DOCX 路径不是文件: {self.docx_path}")

        try:
            document = DocxDocument(self.docx_path)  # 打开DOCX
        except Exception as exc:
            raise RuntimeError(f"打开 DOCX 文件失败: {self.docx_path}") from exc

        results: List[Dict[str, Union[str, int]]] = []
        try:
            for index, paragraph in enumerate(document.paragraphs, start=1):
                text = paragraph.text.strip()
                if not text:  # 跳过空段落
                    continue
                results.append(
                    {
                        "text": text,
                        "paragraph": index,  # 段落序号
                        "source": self.docx_path.name,  # 文件名
                    }
                )
            return results
        except Exception as exc:
            raise RuntimeError(f"解析 DOCX 内容失败: {self.docx_path}") from exc