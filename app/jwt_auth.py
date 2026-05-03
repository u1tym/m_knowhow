from fastapi import HTTPException, Request, status
import jwt
from jwt.exceptions import PyJWTError

from app.config import get_settings


def get_jwt_from_cookie(request: Request) -> str | None:
    return request.cookies.get(get_settings().cookie_name)


def decode_verified_jwt(token: str) -> dict:
    settings = get_settings()
    if not settings.secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="サーバ設定不備です。",
        )
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
    except PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです。",
        ) from e


def username_from_claims(claims: dict) -> str:
    raw = claims.get("username")
    if not isinstance(raw, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名クレームが不正です。",
        )
    name = raw.strip()
    if not name:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名クレームが不正です。",
        )
    return name


def verified_username_from_request(request: Request) -> str:
    token = get_jwt_from_cookie(request)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未認証です。",
        )
    claims = decode_verified_jwt(token)
    return username_from_claims(claims)
