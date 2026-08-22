import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, require_enrollment
from app.crud import content_item as content_item_crud
from app.crud import course as course_crud
from app.crud import enrollment as enrollment_crud
from app.crud import progress as progress_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.progress import CourseProgressSummary, DashboardResponse, TopicProgressSummary

router = APIRouter(tags=["progress"])


@router.post("/content-items/{item_id}/complete", status_code=status.HTTP_204_NO_CONTENT)
async def complete_content_item(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_enrollment),
):
    item = await content_item_crud.get_by_id(db, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Материал не найден")
    await progress_crud.mark_completed(db, user_id=user.id, content_item_id=item_id)


@router.get("/courses/{course_id}/my-progress", response_model=list[uuid.UUID])
async def get_my_course_progress(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    course = await course_crud.get_by_id(db, course_id, with_topics=True)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Курс не найден")

    all_item_ids = [item.id for topic in course.topics for item in topic.content_items]
    completed_ids = await progress_crud.get_completed_item_ids(db, user_id=user.id, content_item_ids=all_item_ids)
    return list(completed_ids)


@router.get("/users/me/dashboard", response_model=DashboardResponse)
async def get_dashboard(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    enrollments = await enrollment_crud.list_enrollments_for_user(db, user.id)

    course_summaries: list[CourseProgressSummary] = []
    for enrollment in enrollments:
        course = await course_crud.get_by_id(db, enrollment.course_id, with_topics=True)
        if course is None:
            continue

        all_item_ids = [item.id for topic in course.topics for item in topic.content_items]
        completed_ids = await progress_crud.get_completed_item_ids(
            db, user_id=user.id, content_item_ids=all_item_ids
        )

        topic_summaries = [
            TopicProgressSummary(
                topic_id=topic.id,
                title=topic.title,
                total_items=len(topic.content_items),
                completed_items=sum(1 for item in topic.content_items if item.id in completed_ids),
            )
            for topic in course.topics
        ]

        total_items = len(all_item_ids)
        completed_items = len(completed_ids)
        percent = round(completed_items / total_items * 100) if total_items else 0

        course_summaries.append(
            CourseProgressSummary(
                course_id=course.id,
                title=course.title,
                slug=course.slug,
                cover_image_path=course.cover_image_path,
                price=course.price,
                total_items=total_items,
                completed_items=completed_items,
                percent=percent,
                topics=topic_summaries,
            )
        )

    return DashboardResponse(courses=course_summaries)
