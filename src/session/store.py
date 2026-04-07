"""インメモリセッションストア + TTL管理"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Literal

from src.config import SESSION_TTL_SECONDS

logger = logging.getLogger(__name__)

SessionState = Literal["idle", "practicing", "scoring"]


@dataclass
class Message:
    role: Literal["user", "assistant"]
    content: str


@dataclass
class Session:
    user_id: str
    state: SessionState = "idle"
    history: list[Message] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    last_active_at: datetime = field(default_factory=datetime.utcnow)
    last_expression: str = "neutral"

    def touch(self) -> None:
        self.last_active_at = datetime.utcnow()

    def reset(self) -> None:
        self.state = "idle"
        self.history = []
        self.started_at = datetime.utcnow()
        self.last_expression = "neutral"
        self.touch()

    def to_messages(self) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in self.history]


_sessions: dict[str, Session] = {}


def get_session(user_id: str) -> Session:
    session = _sessions.get(user_id)
    if session is None:
        session = Session(user_id=user_id)
        _sessions[user_id] = session
        logger.info("新規セッション作成: user_id=%s", user_id)
    session.touch()
    return session


def reset_session(user_id: str) -> Session:
    session = get_session(user_id)
    session.reset()
    return session


def cleanup_expired_sessions() -> int:
    now = datetime.utcnow()
    expired_ids = [
        uid for uid, s in _sessions.items() if now - s.last_active_at > timedelta(seconds=SESSION_TTL_SECONDS)
    ]
    for uid in expired_ids:
        del _sessions[uid]
    if expired_ids:
        logger.info("期限切れセッション削除: %d件", len(expired_ids))
    return len(expired_ids)


async def cleanup_loop(interval_seconds: int = 300) -> None:
    """5分ごとに期限切れセッションをクリーンアップするバックグラウンドタスク"""
    while True:
        try:
            await asyncio.sleep(interval_seconds)
            cleanup_expired_sessions()
        except asyncio.CancelledError:
            logger.info("セッションクリーンアップループ停止")
            raise
        except Exception as exc:  # noqa: BLE001
            logger.exception("セッションクリーンアップで例外: %s", exc)
