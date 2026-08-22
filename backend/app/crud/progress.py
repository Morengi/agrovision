import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import ContentItemProgress, ProgressStatus


async def get_progress(db: AsyncSession, *, user_id: uuid.UUID, content_item_id: uuid.UUID) -> ContentItemProgress | None:
    result = await db.execute(
        select(ContentItemProgress).where(
            ContentItemProgress.user_id == user_id, ContentItemProgress.content_item_id == content_item_id
        )
    )
    return result.scalar_one_or_none()


async def mark_completed(db: AsyncSession, *, user_id: uuid.UUID, content_item_id: uuid.UUID) -> ContentItemProgress:
    existing = await get_progress(db, user_id=user_id, content_item_id=content_item_id)
    if existing is not None:
        return existing

    progress = ContentItemProgress(
        user_id=user_id,
        content_item_id=content_item_id,
        status=ProgressStatus.completed,
        completed_at=datetime.now(timezone.utc),
    )
    db.add(progress)
    await db.commit()
    await db.refresh(progress)
    return progress


async def get_completed_item_ids(db: AsyncSession, *, user_id: uuid.UUID, content_item_ids: list[uuid.UUID]) -> set[uuid.UUID]:
    if not content_item_ids:
        return set()
    result = await db.execute(
        select(ContentItemProgress.content_item_id).where(
            ContentItemProgress.user_id == user_id,
            ContentItemProgress.content_item_id.in_(content_item_ids),
            ContentItemProgress.status == ProgressStatus.completed,
        )
    )
    return set(result.scalars().all())
