"""LINE Webhookハンドラー（イベント処理本体）"""

import logging

from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    QuickReply,
    QuickReplyItem,
    MessageAction,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import FollowEvent, MessageEvent, TextMessageContent

from src.ai.patient import continue_practice, start_practice
from src.ai.scoring import call_scoring_ai
from src.config import LINE_CHANNEL_ACCESS_TOKEN, MAX_USER_MESSAGE_LENGTH
from src.session.store import Session, get_session, reset_session
from src.utils.triggers import detect_trigger

logger = logging.getLogger(__name__)

_config = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
_messaging_api: AsyncMessagingApi | None = None


def _get_messaging_api() -> AsyncMessagingApi:
    """AsyncApiClient はイベントループ内で初期化する必要があるため遅延生成"""
    global _messaging_api
    if _messaging_api is None:
        _messaging_api = AsyncMessagingApi(AsyncApiClient(_config))
    return _messaging_api


# ─────────────────────────────────────────────
# Quick Reply 定義
# ─────────────────────────────────────────────
def _quick_reply_idle() -> QuickReply:
    """idle状態用: 練習を始めるボタン"""
    return QuickReply(
        items=[
            QuickReplyItem(action=MessageAction(label="▶ 練習開始", text="練習開始")),
        ]
    )


def _quick_reply_practicing() -> QuickReply:
    """practicing状態用: 採点・リセット"""
    return QuickReply(
        items=[
            QuickReplyItem(action=MessageAction(label="📝 採点して", text="採点して")),
            QuickReplyItem(action=MessageAction(label="🔄 リセット", text="リセット")),
        ]
    )


def _quick_reply_after_scoring() -> QuickReply:
    """採点後: もう一度練習する誘導"""
    return QuickReply(
        items=[
            QuickReplyItem(action=MessageAction(label="▶ もう一度練習する", text="練習開始")),
        ]
    )


# ─────────────────────────────────────────────
# 返信ヘルパー
# ─────────────────────────────────────────────
async def _reply(reply_token: str, text: str, quick_reply: QuickReply | None = None) -> None:
    message = TextMessage(text=text, quickReply=quick_reply)
    await _get_messaging_api().reply_message(ReplyMessageRequest(reply_token=reply_token, messages=[message]))


# ─────────────────────────────────────────────
# メッセージ定数
# ─────────────────────────────────────────────
WELCOME_MESSAGE = (
    "はじめまして！『練習お客様AI』へようこそ🩺\n\n"
    "ここは、カイロプラクター見習いの先生のための\n"
    "初回カウンセリング練習ボットです。\n\n"
    "▼ 使い方\n"
    "①「練習開始」で患者役（田中美咲さん）が来院します\n"
    "② 自然な問診を10分ほど行ってください\n"
    "③「採点して」で5項目の採点フィードバックが届きます\n\n"
    "下のボタンからすぐに始められます👇"
)

RESET_MESSAGE = "セッションをリセットしました。準備ができたら「練習開始」を押してください。"
ALREADY_PRACTICING_NOTE = "（練習中です。続けて先生の質問をどうぞ）"
ERROR_MESSAGE = "ただいま混雑しています。少し時間をおいて再送してください🙏"


# ─────────────────────────────────────────────
# イベントハンドラー
# ─────────────────────────────────────────────
async def handle_follow(event: FollowEvent) -> None:
    """友だち追加: ウェルカム送信"""
    user_id = event.source.user_id if event.source else "unknown"
    logger.info("Followイベント: user_id=%s", user_id)
    if user_id != "unknown":
        reset_session(user_id)
    await _reply(event.reply_token, WELCOME_MESSAGE, _quick_reply_idle())


async def handle_message(event: MessageEvent) -> None:
    """テキストメッセージ処理"""
    if not isinstance(event.message, TextMessageContent):
        return  # 非テキストは無視

    user_id = event.source.user_id if event.source else None
    if not user_id:
        logger.warning("user_id取得不可。スキップ")
        return

    text = event.message.text[:MAX_USER_MESSAGE_LENGTH]
    trigger = detect_trigger(text)
    session = get_session(user_id)

    logger.info("メッセージ受信: user_id=%s state=%s trigger=%s", user_id, session.state, trigger)

    try:
        if trigger == "reset":
            reset_session(user_id)
            await _reply(event.reply_token, RESET_MESSAGE, _quick_reply_idle())
            return

        if trigger == "start":
            greeting = start_practice(session)
            await _reply(event.reply_token, greeting, _quick_reply_practicing())
            return

        if trigger == "score":
            if session.state != "practicing" or not session.history:
                await _reply(
                    event.reply_token,
                    "まだ練習が始まっていません。「練習開始」から始めてください。",
                    _quick_reply_idle(),
                )
                return
            session.state = "scoring"
            scoring_text = call_scoring_ai(session)
            reset_session(user_id)
            await _reply(event.reply_token, scoring_text, _quick_reply_after_scoring())
            return

        # continue: 通常の対話
        if session.state != "practicing":
            await _reply(
                event.reply_token,
                "練習はまだ始まっていません。下のボタンから「練習開始」を押してください。",
                _quick_reply_idle(),
            )
            return

        reply_text = continue_practice(session, text)
        await _reply(event.reply_token, reply_text, _quick_reply_practicing())

    except Exception as exc:  # noqa: BLE001
        logger.exception("メッセージ処理で例外: user_id=%s err=%s", user_id, exc)
        try:
            await _reply(event.reply_token, ERROR_MESSAGE, _quick_reply_idle())
        except Exception:  # noqa: BLE001
            logger.exception("エラー返信にも失敗")


# 露出: テスト・main から参照
__all__ = ["handle_follow", "handle_message", "Session"]
