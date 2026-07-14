"""
DocMind 后端入口文件
====================
这是整个后端的"大门"，所有请求都从这里进入。

它做了这几件事：
1. 创建 FastAPI 应用实例
2. 在应用启动时初始化日志和数据库
3. 注册中间件（日志记录 + 跨域支持）
4. 注册所有 API 路由
5. 托管前端静态文件（生产模式下前后端合并部署）
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 导入各个 API 路由模块
from app.api.health import router as health_router
from app.api.upload import router as upload_router
from app.api.documents import router as documents_router
from app.api.chat import router as chat_router
from app.api.chat_stream import router as chat_stream_router
from app.api.search import router as search_router
from app.api.history import router as history_router
from app.api.auth import router as auth_router

# 导入配置和工具
from app.core.config import APP_DEBUG
from app.core.logging import setup_logging
from app.core.middleware import RequestLogMiddleware
from app.db.database import init_db

# 静态文件目录：指向 backend/static/，存放前端构建产物
# Path(__file__) 是当前文件 main.py 的路径
# .resolve().parents[1] 往上一级就是 backend/ 目录
STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


# ============================================================
# 应用生命周期管理
# ============================================================
# lifespan 是 FastAPI 的生命周期管理机制：
#   - yield 之前的代码在应用启动时执行
#   - yield 之后的代码在应用关闭时执行
# 这里我们在启动时初始化日志和数据库
@asynccontextmanager
async def lifespan(application: FastAPI):
    # 启动时：配置日志格式 + 创建数据库表
    setup_logging()
    init_db()
    yield  # 应用运行中...直到关闭


# ============================================================
# 创建 FastAPI 应用实例
# ============================================================
app = FastAPI(
    title="DocMind API",       # API 文档标题
    version="0.1.0",           # 版本号
    lifespan=lifespan,         # 绑定生命周期管理
)

# ============================================================
# 注册中间件
# ============================================================
# 中间件就像"安检"，每个请求进来都要先过中间件这一关

# 1. 请求日志中间件：记录每个请求的方法、路径、状态码、耗时
app.add_middleware(RequestLogMiddleware)

# 2. CORS 中间件：允许前端跨域访问后端
#    开发时前端跑在 5173 端口，后端跑在 8000 端口，属于跨域
#    生产模式下前后端同端口，其实不需要，但加上也不影响
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # 允许所有来源（生产环境建议限制具体域名）
    allow_credentials=True,    # 允许携带 Cookie
    allow_methods=["*"],       # 允许所有 HTTP 方法
    allow_headers=["*"],       # 允许所有请求头
)

# ============================================================
# 注册 API 路由
# ============================================================
# 每个路由模块负责一类功能，统一挂载到 /api 前缀下
# 例如 health_router 里的 /health 就变成 /api/health
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(chat_stream_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(history_router, prefix="/api")

# ============================================================
# 托管前端静态文件
# ============================================================
# 生产模式下，前端构建后的 HTML/CSS/JS 文件放在 static/ 目录
# FastAPI 直接提供这些文件，这样只需要启动一个服务

# 挂载 /assets 目录，提供 JS/CSS 等静态资源
app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")


@app.get("/")
async def serve_index():
    """访问根路径时返回 Vue 应用的 index.html"""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """
    SPA 回退路由：所有未匹配的路径都返回 index.html

    为什么需要这个？因为 Vue Router 使用 history 模式，
    用户直接访问 /chat 时，服务器需要返回 index.html，
    然后由前端 JavaScript 来解析路由并渲染对应页面。

    如果没有这个路由，直接访问 /chat 会返回 404。
    """
    file_path = STATIC_DIR / full_path
    # 如果请求的是真实存在的静态文件（如 JS/CSS），直接返回
    if file_path.is_file():
        return FileResponse(file_path)
    # 否则返回 index.html，交给 Vue Router 处理
    return FileResponse(STATIC_DIR / "index.html")