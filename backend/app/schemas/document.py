"""
文档相关的数据校验模型
======================
定义文档列表、详情、上传等 API 的响应格式。

为什么有这么多模型？
- 列表页只需要基本信息（名称、类型、时间）
- 详情页需要更多信息（包括分块内容）
- 上传成功只需要返回文档 ID 和文件名
- 不同场景返回不同数据，避免泄露不必要的信息
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class DocumentListItem(BaseModel):
    """文档列表项：用于文档列表页，只包含基本信息"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_name: str
    file_type: str
    upload_time: datetime


class DocumentChunkInfo(BaseModel):
    """文档分块信息：用于文档详情页，展示文档被切分后的内容"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    chunk_index: int           # 分块序号
    content: str               # 分块文本内容
    metadata: Optional[Dict[str, Any]] = None  # 元数据（页码、来源等）


class DocumentDetailResponse(DocumentListItem):
    """文档详情响应：继承列表项，额外包含分块信息"""
    chunks: List[DocumentChunkInfo] = []  # 该文档的所有分块


class DocumentUploadResponse(BaseModel):
    """文档上传响应：上传成功后返回"""
    success: bool         # 是否上传成功
    document_id: int      # 文档在数据库中的 ID
    filename: str         # 文件名