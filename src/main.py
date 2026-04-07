"""FastAPIエントリーポイント"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, Request
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhook import WebhookParser
from linebot.v3.webhooks import FollowEvent, MessageEvent

from src.config import LINE_CHANNEL_SECRET
from src.session.store import cleanup_loop
from src.webhook.line_handler import handle_follow, handle_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

_parser = WebhookParser(LINE_CHANNEL_SECRET)


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


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/webhook/line")
async def webhook_line(
    request: Request,
    x_line_signature: str = Header(..., alias="X-Line-Signature"),
) -> dict:
    body_bytes = await request.body()
    body_text = body_bytes.decode("utf-8")

    try:
        events = _parser.parse(body_text, x_line_signature)
    except InvalidSignatureError:
        logger.warning("LINE署名検証失敗")
        raise HTTPException(status_code=401, detail="Invalid signature")

    for event in events:
        try:
            if isinstance(event, FollowEvent):
                await handle_follow(event)
            elif isinstance(event, MessageEvent):
                await handle_message(event)
            else:
                logger.info("非対応イベント: %s", type(event).__name__)
        except Exception as exc:  # noqa: BLE001
            logger.exception("イベント処理で例外: %s", exc)

    return {"status": "ok"}
