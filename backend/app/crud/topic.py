import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.course import next_topic_order_index
from app.models.topic import Topic


async def get_by_id(db: AsyncSession, topic_id: uuid.UUID) -> Topic | None:
    return await db.get(Topic, topic_id)


async def list_by_course(db: AsyncSession, course_id: uuid.UUID) -> list[Topic]:
    result = await db.execute(
        select(Topic).where(Topic.course_id == course_id).order_by(Topic.order_index)
    )
    return list(result.scalars().all())


async def create_topic(
    db: AsyncSession, *, course_id: uuid.UUID, title: str, description: str, order_index: int | None
) -> Topic:
    if order_index is None:
        order_index = await next_topic_order_index(db, course_id)

    topic = Topic(course_id=course_id, title=title, description=description, order_index=order_index)
    db.add(topic)
    await db.commit()
    await db.refresh(topic)
    return topic


async def update_topic(
    db: AsyncSession,
    topic: Topic,
    *,
    title: str | None = None,
    description: str | None = None,
    order_index: int | None = None,
) -> Topic:
    if title is not None:
        topic.title = title
    if description is not None:
        topic.description = description
    if order_index is not None:
        topic.order_index = order_index

    await db.commit()
    await db.refresh(topic)
    return topic


async def delete_topic(db: AsyncSession, topic: Topic) -> None:
    await db.delete(topic)
    await db.commit()


async def get_course_id_for_content_item(db: AsyncSession, content_item_id: uuid.UUID) -> uuid.UUID | None:
    from app.models.content_item import ContentItem  # local import avoids a circular import at module load

    result = await db.execute(
        select(Topic.course_id).join(ContentItem, ContentItem.topic_id == Topic.id).where(
            ContentItem.id == content_item_id
        )
    )
    return result.scalar_one_or_none()
