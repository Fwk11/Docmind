from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.health import router as health_router
from app.api.upload import router as upload_router
from app.api.documents import router as documents_router
from app.api.chat import router as chat_router
from app.api.chat_stream import router as chat_stream_router
from app.api.search import router as search_router
from app.api.history import router as history_router
from app.api.auth import router as auth_router
from app.core.config import APP_DEBUG
from app.core.logging import setup_logging
from app.core.middleware import RequestLogMiddleware
from app.db.database import init_db

STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


@asynccontextmanager
async def lifespan(application: FastAPI):
    setup_logging()
    init_db()
    yield


app = FastAPI(title="DocMind API", version="0.1.0", lifespan=lifespan)

app.add_middleware(RequestLogMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(chat_stream_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(history_router, prefix="/api")

app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")


@app.get("/")
async def serve_index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    file_path = STATIC_DIR / full_path
    if file_path.is_file():
        return FileResponse(file_path)
    return FileResponse(STATIC_DIR / "index.html")