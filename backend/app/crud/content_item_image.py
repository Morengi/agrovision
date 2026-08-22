import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content_item_image import ContentItemImage


async def get_by_id(db: AsyncSession, image_id: uuid.UUID) -> ContentItemImage | None:
    return await db.get(ContentItemImage, image_id)


async def next_order_index(db: AsyncSession, content_item_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.coalesce(func.max(ContentItemImage.order_index), -1)).where(
            ContentItemImage.content_item_id == content_item_id
        )
    )
    return result.scalar_one() + 1


async def add_image(db: AsyncSession, *, content_item_id: uuid.UUID, image_path: str) -> ContentItemImage:
    order_index = await next_order_index(db, content_item_id)
    image = ContentItemImage(content_item_id=content_item_id, image_path=image_path, order_index=order_index)
    db.add(image)
    await db.commit()
    await db.refresh(image)
    return image


async def delete_image(db: AsyncSession, image: ContentItemImage) -> None:
    await db.delete(image)
    await db.commit()
