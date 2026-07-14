from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class DocumentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_name: str
    file_type: str
    upload_time: datetime


class DocumentChunkInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chunk_index: int
    content: str
    metadata: Optional[Dict[str, Any]] = None


class DocumentDetailResponse(DocumentListItem):
    chunks: List[DocumentChunkInfo] = []


class DocumentUploadResponse(BaseModel):
    success: bool
    document_id: int
    filename: str