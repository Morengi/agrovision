import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.slugify import slugify
from app.models.tag import Tag


async def list_tags(db: AsyncSession) -> list[Tag]:
    result = await db.execute(select(Tag).order_by(Tag.name))
    return list(result.scalars().all())


async def get_by_ids(db: AsyncSession, tag_ids: list[uuid.UUID]) -> list[Tag]:
    if not tag_ids:
        return []
    result = await db.execute(select(Tag).where(Tag.id.in_(tag_ids)))
    return list(result.scalars().all())


async def get_by_slug(db: AsyncSession, slug: str) -> Tag | None:
    result = await db.execute(select(Tag).where(Tag.slug == slug))
    return result.scalar_one_or_none()


async def create_tag(db: AsyncSession, name: str) -> Tag:
    base_slug = slugify(name)
    slug = base_slug
    suffix = 1
    while await get_by_slug(db, slug) is not None:
        suffix += 1
        slug = f"{base_slug}-{suffix}"

    tag = Tag(name=name, slug=slug)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag
