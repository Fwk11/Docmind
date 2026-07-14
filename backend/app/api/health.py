# 这是健康检查接口模块，用于验证服务是否正常启动。
from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    """返回服务健康状态，便于部署和调试。"""
    return {"status": "ok", "app": "DocMind"}
