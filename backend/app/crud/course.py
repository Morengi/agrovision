import uuid
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.slugify import slugify
from app.crud import tag as tag_crud
from app.models.course import Course, course_tags
from app.models.tag import Tag
from app.models.topic import Topic


async def _unique_slug(db: AsyncSession, title: str) -> str:
    base_slug = slugify(title)
    slug = base_slug
    suffix = 1
    while await get_by_slug(db, slug) is not None:
        suffix += 1
        slug = f"{base_slug}-{suffix}"
    return slug


async def get_by_slug(db: AsyncSession, slug: str, *, with_topics: bool = False) -> Course | None:
    stmt = select(Course).where(Course.slug == slug)
    if with_topics:
        stmt = stmt.options(selectinload(Course.topics).selectinload(Topic.content_items))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_id(db: AsyncSession, course_id: uuid.UUID, *, with_topics: bool = False) -> Course | None:
    stmt = select(Course).where(Course.id == course_id)
    if with_topics:
        stmt = stmt.options(selectinload(Course.topics).selectinload(Topic.content_items))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_courses(
    db: AsyncSession,
    *,
    search: str | None = None,
    is_free: bool | None = None,
    tag_slugs: list[str] | None = None,
    published_only: bool = True,
    page: int = 1,
    page_size: int = 12,
) -> tuple[list[Course], int]:
    stmt = select(Course)

    if published_only:
        stmt = stmt.where(Course.is_published.is_(True))
    if search:
        stmt = stmt.where(Course.title.ilike(f"%{search}%"))
    if is_free is True:
        stmt = stmt.where(Course.price == Decimal("0"))
    elif is_free is False:
        stmt = stmt.where(Course.price > Decimal("0"))
    if tag_slugs:
        stmt = (
            stmt.join(course_tags, course_tags.c.course_id == Course.id)
            .join(Tag, Tag.id == course_tags.c.tag_id)
            .where(Tag.slug.in_(tag_slugs))
            .distinct()
        )

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = stmt.order_by(Course.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def create_course(
    db: AsyncSession, *, title: str, description: str, price: Decimal, tag_ids: list[uuid.UUID], created_by: uuid.UUID
) -> Course:
    slug = await _unique_slug(db, title)
    tags = await tag_crud.get_by_ids(db, tag_ids)
    course = Course(
        title=title,
        slug=slug,
        description=description,
        price=price,
        created_by=created_by,
        tags=tags,
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


async def update_course(
    db: AsyncSession,
    course: Course,
    *,
    title: str | None = None,
    description: str | None = None,
    price: Decimal | None = None,
    is_published: bool | None = None,
    tag_ids: list[uuid.UUID] | None = None,
) -> Course:
    if title is not None and title != course.title:
        course.title = title
        course.slug = await _unique_slug(db, title)
    if description is not None:
        course.description = description
    if price is not None:
        course.price = price
    if is_published is not None:
        course.is_published = is_published
    if tag_ids is not None:
        course.tags = await tag_crud.get_by_ids(db, tag_ids)

    await db.commit()
    await db.refresh(course)
    return course


async def delete_course(db: AsyncSession, course: Course) -> None:
    await db.delete(course)
    await db.commit()


async def next_topic_order_index(db: AsyncSession, course_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.coalesce(func.max(Topic.order_index), -1)).where(Topic.course_id == course_id)
    )
    return result.scalar_one() + 1
