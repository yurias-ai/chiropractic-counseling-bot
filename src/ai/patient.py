"""患者役Claude呼び出し"""

import logging

from anthropic import Anthropic

from src.ai.prompts import PATIENT_INITIAL_GREETING_TRIGGER, PATIENT_SYSTEM_PROMPT
from src.config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from src.session.store import Message, Session

logger = logging.getLogger(__name__)

_client = Anthropic(api_key=ANTHROPIC_API_KEY)


def call_patient_ai(session: Session) -> str:
    """会話履歴を渡して患者役の応答を生成する"""
    messages = session.to_messages()
    if not messages:
        # セッション開始時の初回挨拶
        messages = [{"role": "user", "content": PATIENT_INITIAL_GREETING_TRIGGER}]

    response = _client.messages.create(
        model=CLAUDE_MODEL,
        system=PATIENT_SYSTEM_PROMPT,
        messages=messages,
        max_tokens=400,
    )
    text = "".join(block.text for block in response.content if hasattr(block, "text")).strip()
    logger.info("患者役応答生成: user_id=%s len=%d", session.user_id, len(text))
    return text


def start_practice(session: Session) -> str:
    """練習開始: セッションをリセットし、患者役の初回挨拶を生成"""
    session.reset()
    session.state = "practicing"
    greeting = call_patient_ai(session)
    session.history.append(Message(role="assistant", content=greeting))
    return greeting


def continue_practice(session: Session, user_text: str) -> str:
    """練習継続: ユーザー発言を履歴に追加し、患者役の応答を生成"""
    session.history.append(Message(role="user", content=user_text))
    reply = call_patient_ai(session)
    session.history.append(Message(role="assistant", content=reply))
    return reply
