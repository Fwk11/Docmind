"""
健康检查响应模型
================
定义健康检查接口的返回格式。

健康检查接口是给运维用的，用来确认服务是否正常运行。
比如 Docker 或 Kubernetes 会定期调用这个接口，
如果返回 200 就说明服务还活着，否则就重启它。
"""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str   # 服务状态，正常时返回 "ok"
    app: str      # 应用名称，返回 "DocMind"