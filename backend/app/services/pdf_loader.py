# 这是 PDF 文档加载服务模块，负责读取 PDF 文件并按页提取文本。
from pathlib import Path
from typing import List, Dict, Any, Union

import fitz  # PyMuPDF


class PDFLoaderService:
    """用于将 PDF 文件内容按页拆分成结构化文本的服务类。"""

    def __init__(self, pdf_path: Union[str, Path]):
        """初始化服务时保存 PDF 文件路径。"""
        self.pdf_path = Path(pdf_path)

    def load(self) -> List[Dict[str, Any]]:
        """读取 PDF 文件并返回包含文本、页码、来源文件名的列表。"""
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF 文件不存在: {self.pdf_path}")

        if not self.pdf_path.is_file():
            raise ValueError(f"PDF 路径不是文件: {self.pdf_path}")

        try:
            document = fitz.open(self.pdf_path)
        except Exception as exc:
            raise RuntimeError(f"打开 PDF 文件失败: {self.pdf_path}") from exc

        try:
            results: List[Dict[str, Any]] = []
            for page_num in range(document.page_count):
                page = document.load_page(page_num)
                text = page.get_text("text")
                results.append(
                    {
                        "text": text.strip(),
                        "page": page_num + 1,
                        "source": self.pdf_path.name,
                    }
                )
            return results
        except Exception as exc:
            raise RuntimeError(f"解析 PDF 文本失败: {self.pdf_path}") from exc
        finally:
            document.close()
