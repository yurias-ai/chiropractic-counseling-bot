"""環境変数集約モジュール（os.environ アクセスはここのみ）"""

import os
from pathlib import Path

from dotenv import load_dotenv

# .env.local をプロジェクトルートから読み込み
_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_ROOT / ".env.local")


def _required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"環境変数 {name} が設定されていません。.env.local を確認してください。")
    return value


LINE_CHANNEL_SECRET: str = _required("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN: str = _required("LINE_CHANNEL_ACCESS_TOKEN")
ANTHROPIC_API_KEY: str = _required("ANTHROPIC_API_KEY")

PORT: int = int(os.environ.get("PORT", "8940"))
SESSION_TTL_SECONDS: int = int(os.environ.get("SESSION_TTL_SECONDS", "3600"))

CLAUDE_MODEL: str = "claude-sonnet-4-5"
MAX_USER_MESSAGE_LENGTH: int = 5000
