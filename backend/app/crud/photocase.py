import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.photocase import PhotocaseOption


async def get_by_id(db: AsyncSession, option_id: uuid.UUID) -> PhotocaseOption | None:
    return await db.get(PhotocaseOption, option_id)


async def list_by_content_item(db: AsyncSession, content_item_id: uuid.UUID) -> list[PhotocaseOption]:
    result = await db.execute(
        select(PhotocaseOption)
        .where(PhotocaseOption.content_item_id == content_item_id)
        .order_by(PhotocaseOption.order_index)
    )
    return list(result.scalars().all())


async def next_order_index(db: AsyncSession, content_item_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.coalesce(func.max(PhotocaseOption.order_index), -1)).where(
            PhotocaseOption.content_item_id == content_item_id
        )
    )
    return result.scalar_one() + 1


async def create_option(
    db: AsyncSession,
    *,
    content_item_id: uuid.UUID,
    label: str,
    is_correct: bool,
    explanation: str,
    order_index: int | None,
) -> PhotocaseOption:
    if order_index is None:
        order_index = await next_order_index(db, content_item_id)

    option = PhotocaseOption(
        content_item_id=content_item_id,
        label=label,
        is_correct=is_correct,
        explanation=explanation,
        order_index=order_index,
    )
    db.add(option)
    await db.commit()
    await db.refresh(option)
    return option


async def update_option(
    db: AsyncSession,
    option: PhotocaseOption,
    *,
    label: str | None = None,
    is_correct: bool | None = None,
    explanation: str | None = None,
    order_index: int | None = None,
) -> PhotocaseOption:
    if label is not None:
        option.label = label
    if is_correct is not None:
        option.is_correct = is_correct
    if explanation is not None:
        option.explanation = explanation
    if order_index is not None:
        option.order_index = order_index

    await db.commit()
    await db.refresh(option)
    return option


async def delete_option(db: AsyncSession, option: PhotocaseOption) -> None:
    await db.delete(option)
    await db.commit()
