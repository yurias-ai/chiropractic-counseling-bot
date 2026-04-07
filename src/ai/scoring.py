"""採点役Claude呼び出し"""

import logging

from anthropic import Anthropic

from src.ai.prompts import SCORING_SYSTEM_PROMPT
from src.config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from src.session.store import Session

logger = logging.getLogger(__name__)

_client = Anthropic(api_key=ANTHROPIC_API_KEY)


def _format_history_as_text(session: Session) -> str:
    lines = []
    for msg in session.history:
        speaker = "先生" if msg.role == "user" else "患者（田中美咲）"
        lines.append(f"{speaker}: {msg.content}")
    return "\n".join(lines)


def call_scoring_ai(session: Session) -> str:
    """会話履歴をテキスト化して採点役に渡す"""
    if not session.history:
        return "■ 採点結果\n会話がまだありません。「練習開始」から始めてください。"

    history_text = _format_history_as_text(session)
    response = _client.messages.create(
        model=CLAUDE_MODEL,
        system=SCORING_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"以下の会話を採点してください。\n\n---\n{history_text}\n---",
            }
        ],
        max_tokens=1500,
    )
    text = "".join(block.text for block in response.content if hasattr(block, "text")).strip()
    logger.info("採点生成: user_id=%s len=%d", session.user_id, len(text))
    return text
