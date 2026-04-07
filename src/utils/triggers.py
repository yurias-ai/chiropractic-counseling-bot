"""トリガーワード検出（T-002）"""

from typing import Literal

TriggerType = Literal["start", "score", "reset", "continue"]

_START_KEYWORDS = ("練習開始", "開始", "スタート", "start")
_SCORE_KEYWORDS = ("採点して", "採点", "評価", "フィードバック")
_RESET_KEYWORDS = ("リセット", "やり直し", "reset")


def detect_trigger(text: str) -> TriggerType:
    normalized = text.strip().lower()
    if any(k.lower() in normalized for k in _START_KEYWORDS):
        return "start"
    if any(k.lower() in normalized for k in _SCORE_KEYWORDS):
        return "score"
    if any(k.lower() in normalized for k in _RESET_KEYWORDS):
        return "reset"
    return "continue"
