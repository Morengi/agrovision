import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_role
from app.crud import topic as topic_crud
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.topic import TopicCreate, TopicRead, TopicUpdate

router = APIRouter(tags=["topics"])


@router.post("/courses/{course_id}/topics", response_model=TopicRead, status_code=status.HTTP_201_CREATED)
async def create_topic(
    course_id: uuid.UUID,
    payload: TopicCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    topic = await topic_crud.create_topic(
        db,
        course_id=course_id,
        title=payload.title,
        description=payload.description,
        order_index=payload.order_index,
    )
    return TopicRead.model_validate(topic)


@router.patch("/topics/{topic_id}", response_model=TopicRead)
async def update_topic(
    topic_id: uuid.UUID,
    payload: TopicUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    topic = await topic_crud.get_by_id(db, topic_id)
    if topic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена")

    topic = await topic_crud.update_topic(
        db, topic, title=payload.title, description=payload.description, order_index=payload.order_index
    )
    return TopicRead.model_validate(topic)


@router.delete("/topics/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    topic = await topic_crud.get_by_id(db, topic_id)
    if topic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тема не найдена")
    await topic_crud.delete_topic(db, topic)
