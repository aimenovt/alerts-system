from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _is_bcrypt_input_valid(password: str) -> bool:
    return len(password.encode("utf-8")) <= 72


def get_password_hash(password: str) -> str:
    if not _is_bcrypt_input_valid(password):
        raise ValueError("Password is too long for bcrypt (max 72 bytes).")
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not _is_bcrypt_input_valid(plain_password):
        return False
    return password_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode: dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None
