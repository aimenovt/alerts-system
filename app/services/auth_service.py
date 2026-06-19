from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, session: AsyncSession):
        self.users = UserRepository(session)

    async def register_user(self, payload: UserCreate):
        existing = await self.users.get_by_email(payload.email)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        try:
            hashed_password = get_password_hash(payload.password)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

        return await self.users.create(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hashed_password,
        )

    async def authenticate_and_create_token(self, email: str, password: str) -> str | None:
        user = await self.users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            return None

        expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(subject=user.id, expires_delta=expires)
