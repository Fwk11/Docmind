"""
PDF 文档加载模块 — 读取 PDF 文件并按页提取文本

使用 PyMuPDF（fitz）库解析 PDF：
- fitz 是 PyMuPDF 的内部名称，一个高效的 PDF 解析库
- 按页提取文本，每页作为一个独立的文档段落
- 提取结果包含：文本内容、页码、来源文件名

为什么按页提取？
- PDF 通常按页组织内容，按页提取保留结构信息
- 检索时可以知道答案在第几页，方便用户定位
"""
from pathlib import Path
from typing import List, Dict, Any, Union

import fitz  # PyMuPDF：高效的PDF解析库


class PDFLoaderService:
    """PDF加载服务：按页提取文本"""

    def __init__(self, pdf_path: Union[str, Path]):
        """传入PDF文件路径"""
        self.pdf_path = Path(pdf_path)

    def load(self) -> List[Dict[str, Any]]:
        """读取PDF并返回 [{text, page, source}, ...] 列表"""
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF 文件不存在: {self.pdf_path}")

        if not self.pdf_path.is_file():
            raise ValueError(f"PDF 路径不是文件: {self.pdf_path}")

        try:
            document = fitz.open(self.pdf_path)  # 打开PDF
        except Exception as exc:
            raise RuntimeError(f"打开 PDF 文件失败: {self.pdf_path}") from exc

        try:
            results: List[Dict[str, Any]] = []
            for page_num in range(document.page_count):
                page = document.load_page(page_num)  # 加载第N页
                text = page.get_text("text")  # 提取纯文本
                results.append(
                    {
                        "text": text.strip(),
                        "page": page_num + 1,  # 页码从1开始
                        "source": self.pdf_path.name,  # 文件名
                    }
                )
            return results
        except Exception as exc:
            raise RuntimeError(f"解析 PDF 文本失败: {self.pdf_path}") from exc
        finally:
            document.close()  # 确保关闭PDF文件，释放资源