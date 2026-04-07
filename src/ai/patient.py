"""患者役Claude呼び出し（表情タグパース付き）"""

import logging
import re

from anthropic import Anthropic

from src.ai.prompts import PATIENT_INITIAL_GREETING_TRIGGER, PATIENT_SYSTEM_PROMPT
from src.config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from src.session.store import Message, Session

logger = logging.getLogger(__name__)

_client = Anthropic(api_key=ANTHROPIC_API_KEY)

VALID_EXPRESSIONS = {"neutral", "nervous", "worried", "relieved", "thinking"}
_TAG_RE = re.compile(r"^\s*\[\s*(?:表情|expression)\s*[:：]\s*([a-zA-Z]+)\s*\]\s*(.*)$", re.DOTALL)


def parse_expression(raw: str) -> tuple[str, str]:
    """応答テキストから表情タグをパースし (expression, body) を返す。
    タグが無い・不正な場合は ('neutral', body) にフォールバック。
    """
    m = _TAG_RE.match(raw)
    if not m:
        return "neutral", raw.strip()
    expr = m.group(1).lower()
    body = m.group(2).strip()
    if expr not in VALID_EXPRESSIONS:
        return "neutral", body or raw.strip()
    return expr, body


def call_patient_ai(session: Session) -> tuple[str, str]:
    """会話履歴を渡して患者役の応答を生成し (expression, text) を返す"""
    messages = session.to_messages()
    if not messages:
        messages = [{"role": "user", "content": PATIENT_INITIAL_GREETING_TRIGGER}]

    response = _client.messages.create(
        model=CLAUDE_MODEL,
        system=PATIENT_SYSTEM_PROMPT,
        messages=messages,
        max_tokens=400,
    )
    raw = "".join(block.text for block in response.content if hasattr(block, "text")).strip()
    expression, text = parse_expression(raw)
    logger.info("患者役応答生成: user_id=%s expr=%s len=%d", session.user_id, expression, len(text))
    return expression, text


def start_practice(session: Session) -> tuple[str, str]:
    """練習開始: セッションをリセットし、患者役の初回挨拶を生成"""
    session.reset()
    session.state = "practicing"
    expression, text = call_patient_ai(session)
    session.history.append(Message(role="assistant", content=text))
    session.last_expression = expression
    return expression, text


def continue_practice(session: Session, user_text: str) -> tuple[str, str]:
    """練習継続: ユーザー発言を履歴に追加し、患者役の応答を生成"""
    session.history.append(Message(role="user", content=user_text))
    expression, text = call_patient_ai(session)
    session.history.append(Message(role="assistant", content=text))
    session.last_expression = expression
    return expression, text
