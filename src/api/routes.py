"""練習用 HTTP API ルーター"""

from __future__ import annotations

import logging
import uuid

from anthropic import APIError, RateLimitError
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.ai.patient import continue_practice, start_practice
from src.ai.scoring import call_scoring_ai
from src.config import MAX_USER_MESSAGE_LENGTH
from src.session.store import get_session, reset_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/practice", tags=["practice"])


# ─────────────────────────────────────────────
# Request / Response モデル
# ─────────────────────────────────────────────
class StartRequest(BaseModel):
    session_id: str | None = Field(default=None, description="既存セッションID。未指定なら新規発番")


class StartResponse(BaseModel):
    session_id: str
    greeting: str
    state: str


class MessageRequest(BaseModel):
    session_id: str
    text: str = Field(min_length=1, max_length=MAX_USER_MESSAGE_LENGTH)


class MessageResponse(BaseModel):
    reply: str
    state: str


class ScoreRequest(BaseModel):
    session_id: str


class ScoreResponse(BaseModel):
    scoring: str
    turns: int


class ResetRequest(BaseModel):
    session_id: str


class ResetResponse(BaseModel):
    ok: bool = True


# ─────────────────────────────────────────────
# エラーヘルパー
# ─────────────────────────────────────────────
def _wrap_anthropic_call(callable_, *args, **kwargs):
    try:
        return callable_(*args, **kwargs)
    except RateLimitError as exc:
        logger.warning("Anthropic レート制限: %s", exc)
        raise HTTPException(status_code=503, detail="ただいま混雑しています。少し時間をおいて再送してください。")
    except APIError as exc:
        logger.exception("Anthropic API エラー: %s", exc)
        raise HTTPException(status_code=502, detail="AI応答の取得に失敗しました。少し時間をおいて再送してください。")


# ─────────────────────────────────────────────
# エンドポイント
# ─────────────────────────────────────────────
@router.post("/start", response_model=StartResponse)
def start(req: StartRequest) -> StartResponse:
    """練習を開始（または再開始）し、患者役の初回挨拶を返す"""
    session_id = req.session_id or str(uuid.uuid4())
    session = get_session(session_id)
    greeting = _wrap_anthropic_call(start_practice, session)
    return StartResponse(session_id=session_id, greeting=greeting, state=session.state)


@router.post("/message", response_model=MessageResponse)
def message(req: MessageRequest) -> MessageResponse:
    """ユーザーメッセージを送信し、患者役応答を返す"""
    session = get_session(req.session_id)
    if session.state != "practicing":
        raise HTTPException(status_code=400, detail="練習が開始されていません。先に /start を呼んでください。")

    reply = _wrap_anthropic_call(continue_practice, session, req.text.strip())
    return MessageResponse(reply=reply, state=session.state)


@router.post("/score", response_model=ScoreResponse)
def score(req: ScoreRequest) -> ScoreResponse:
    """会話履歴を採点し、結果を返す。採点後セッションは自動リセット"""
    session = get_session(req.session_id)
    if not session.history:
        raise HTTPException(status_code=400, detail="採点対象の会話がまだありません。")

    session.state = "scoring"
    turns = sum(1 for m in session.history if m.role == "user")
    scoring_text = _wrap_anthropic_call(call_scoring_ai, session)
    reset_session(req.session_id)
    return ScoreResponse(scoring=scoring_text, turns=turns)


@router.post("/reset", response_model=ResetResponse)
def reset(req: ResetRequest) -> ResetResponse:
    """セッションを破棄してリセット"""
    reset_session(req.session_id)
    return ResetResponse()
