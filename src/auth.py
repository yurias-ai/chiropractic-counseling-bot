"""HTTP Basic 認証（2ユーザー固定）"""

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from src.config import BASIC_AUTH_USERS

_security = HTTPBasic(realm="Practice Patient AI", auto_error=False)


def verify_user(credentials: HTTPBasicCredentials | None = Depends(_security)) -> str:
    """環境変数 BASIC_AUTH_USERS に登録されたユーザーのみ通す。
    未設定（ローカル開発）の場合は認証スキップ。"""
    if not BASIC_AUTH_USERS:
        return "anonymous"

    if credentials is None:
        raise _unauthorized()

    expected = BASIC_AUTH_USERS.get(credentials.username)
    if expected is None or not secrets.compare_digest(expected, credentials.password):
        raise _unauthorized()

    return credentials.username


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認証に失敗しました",
        headers={"WWW-Authenticate": 'Basic realm="Practice Patient AI"'},
    )
