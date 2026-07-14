"""
健康检查 API 接口
==================
提供 /health 接口，用于检测服务是否正常运行。

这个接口非常简单，但非常重要：
- Docker/Kubernetes 用它来判断容器是否健康
- 负载均衡器用它来决定是否把流量转发给这个实例
- 监控系统用它来报警（如果连续返回非 200 就发告警）
"""

from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    """
    健康检查接口

    返回 {"status": "ok", "app": "DocMind"}
    如果这个接口能正常返回，说明服务还活着。
    """
    return {"status": "ok", "app": "DocMind"}