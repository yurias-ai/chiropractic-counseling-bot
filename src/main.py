"""FastAPIエントリーポイント"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes import router as practice_router
from src.session.store import cleanup_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    cleanup_task = asyncio.create_task(cleanup_loop())
    logger.info("セッションクリーンアップループ起動")
    try:
        yield
    finally:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass
        logger.info("セッションクリーンアップループ停止完了")


app = FastAPI(title="練習お客様AI", lifespan=lifespan)

app.include_router(practice_router)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(_STATIC_DIR / "index.html")


# 静的アセット（あれば）配信。index.html はルートで明示返却するため html=False。
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
