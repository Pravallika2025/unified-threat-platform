from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.core.exceptions import AuthenticationError

ALGORITHM = "HS256"


def _encode(payload: dict, expires: timedelta, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    body = {**payload, "iat": now, "exp": now + expires, "type": token_type}
    return jwt.encode(body, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(*, user_id: str, role: str, environment_id: str | None) -> str:
    return _encode(
        {"sub": user_id, "role": role, "env": environment_id},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "access",
    )


def create_refresh_token(*, user_id: str) -> str:
    return _encode({"sub": user_id}, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), "refresh")


def decode_token(token: str, *, expected_type: str = "access") -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError("Token has expired") from exc
    except jwt.PyJWTError as exc:
        raise AuthenticationError("Invalid token") from exc

    if payload.get("type") != expected_type:
        raise AuthenticationError("Wrong token type")
    return payload
