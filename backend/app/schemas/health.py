# 这是健康检查响应模型，定义返回结构。
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """健康检查接口的响应模型。"""
    status: str
    app: str
