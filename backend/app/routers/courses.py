import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_role
from app.crud import course as course_crud
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.course import CourseCreate, CourseDetail, CourseListItem, CourseUpdate, PaginatedCourses

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=PaginatedCourses)
async def list_courses(
    search: str | None = None,
    is_free: bool | None = None,
    tags: str | None = Query(default=None, description="Comma-separated tag slugs"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    tag_slugs = [t.strip() for t in tags.split(",")] if tags else None
    courses, total = await course_crud.list_courses(
        db,
        search=search,
        is_free=is_free,
        tag_slugs=tag_slugs,
        published_only=True,
        page=page,
        page_size=page_size,
    )
    return PaginatedCourses(
        items=[CourseListItem.model_validate(c) for c in courses], total=total, page=page, page_size=page_size
    )


@router.get("/admin", response_model=PaginatedCourses)
async def list_courses_admin(
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    courses, total = await course_crud.list_courses(
        db, search=search, published_only=False, page=page, page_size=page_size
    )
    return PaginatedCourses(
        items=[CourseListItem.model_validate(c) for c in courses], total=total, page=page, page_size=page_size
    )


@router.get("/admin/{course_id}", response_model=CourseDetail)
async def get_course_admin(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    course = await course_crud.get_by_id(db, course_id, with_topics=True)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Курс не найден")
    return CourseDetail.model_validate(course)


@router.get("/{slug}", response_model=CourseDetail)
async def get_course(slug: str, db: AsyncSession = Depends(get_db)):
    course = await course_crud.get_by_slug(db, slug, with_topics=True)
    if course is None or not course.is_published:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Курс не найден")
    return CourseDetail.model_validate(course)


@router.post("", response_model=CourseDetail, status_code=status.HTTP_201_CREATED)
async def create_course(
    payload: CourseCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    course = await course_crud.create_course(
        db,
        title=payload.title,
        description=payload.description,
        price=payload.price,
        tag_ids=payload.tag_ids,
        created_by=user.id,
    )
    course = await course_crud.get_by_id(db, course.id, with_topics=True)
    return CourseDetail.model_validate(course)


@router.patch("/{course_id}", response_model=CourseDetail)
async def update_course(
    course_id: uuid.UUID,
    payload: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    course = await course_crud.get_by_id(db, course_id, with_topics=True)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Курс не найден")

    course = await course_crud.update_course(
        db,
        course,
        title=payload.title,
        description=payload.description,
        price=payload.price,
        is_published=payload.is_published,
        tag_ids=payload.tag_ids,
    )
    return CourseDetail.model_validate(course)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    course = await course_crud.get_by_id(db, course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Курс не найден")
    await course_crud.delete_course(db, course)
