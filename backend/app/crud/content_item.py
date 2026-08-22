import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.content_item import ContentItem, ContentItemType
from app.models.quiz import QuizQuestion


def _detail_options():
    return (
        selectinload(ContentItem.images),
        selectinload(ContentItem.photocase_options),
        selectinload(ContentItem.quiz_questions).selectinload(QuizQuestion.options),
    )


async def get_by_id(db: AsyncSession, item_id: uuid.UUID) -> ContentItem | None:
    stmt = select(ContentItem).where(ContentItem.id == item_id).options(*_detail_options())
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_by_topic(db: AsyncSession, topic_id: uuid.UUID) -> list[ContentItem]:
    result = await db.execute(
        select(ContentItem).where(ContentItem.topic_id == topic_id).order_by(ContentItem.order_index)
    )
    return list(result.scalars().all())


async def next_order_index(db: AsyncSession, topic_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.coalesce(func.max(ContentItem.order_index), -1)).where(ContentItem.topic_id == topic_id)
    )
    return result.scalar_one() + 1


async def create_content_item(
    db: AsyncSession,
    *,
    topic_id: uuid.UUID,
    type: ContentItemType,
    title: str,
    order_index: int | None,
    text_body: str | None,
) -> ContentItem:
    if order_index is None:
        order_index = await next_order_index(db, topic_id)

    item = ContentItem(topic_id=topic_id, type=type, title=title, order_index=order_index, text_body=text_body)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return await get_by_id(db, item.id)


async def update_content_item(
    db: AsyncSession,
    item: ContentItem,
    *,
    title: str | None = None,
    order_index: int | None = None,
    text_body: str | None = None,
    key_signs: str | None = None,
    next_steps: str | None = None,
) -> ContentItem:
    if title is not None:
        item.title = title
    if order_index is not None:
        item.order_index = order_index
    if text_body is not None:
        item.text_body = text_body
    if key_signs is not None:
        item.key_signs = key_signs
    if next_steps is not None:
        item.next_steps = next_steps

    await db.commit()
    await db.refresh(item)
    return item


async def delete_content_item(db: AsyncSession, item: ContentItem) -> None:
    await db.delete(item)
    await db.commit()
