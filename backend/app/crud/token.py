import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    generate_opaque_token,
    hash_opaque_token,
    refresh_token_expiry,
    reset_token_expiry,
)
from app.models.password_reset_token import PasswordResetToken
from app.models.refresh_token import RefreshToken


async def issue_refresh_token(db: AsyncSession, user_id: uuid.UUID) -> str:
    raw_token = generate_opaque_token()
    token = RefreshToken(
        user_id=user_id,
        token_hash=hash_opaque_token(raw_token),
        expires_at=refresh_token_expiry(),
    )
    db.add(token)
    await db.commit()
    return raw_token


async def get_valid_refresh_token(db: AsyncSession, raw_token: str) -> RefreshToken | None:
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == hash_opaque_token(raw_token))
    )
    token = result.scalar_one_or_none()
    if token is None:
        return None
    if token.revoked_at is not None:
        return None
    if token.expires_at < datetime.now(timezone.utc):
        return None
    return token


async def revoke_refresh_token(db: AsyncSession, token: RefreshToken) -> None:
    token.revoked_at = datetime.now(timezone.utc)
    await db.commit()


async def issue_password_reset_token(db: AsyncSession, user_id: uuid.UUID) -> str:
    raw_token = generate_opaque_token()
    token = PasswordResetToken(
        user_id=user_id,
        token_hash=hash_opaque_token(raw_token),
        expires_at=reset_token_expiry(),
    )
    db.add(token)
    await db.commit()
    return raw_token


async def get_valid_reset_token(db: AsyncSession, raw_token: str) -> PasswordResetToken | None:
    result = await db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == hash_opaque_token(raw_token))
    )
    token = result.scalar_one_or_none()
    if token is None:
        return None
    if token.used_at is not None:
        return None
    if token.expires_at < datetime.now(timezone.utc):
        return None
    return token


async def consume_reset_token(db: AsyncSession, token: PasswordResetToken) -> None:
    token.used_at = datetime.now(timezone.utc)
    await db.commit()
