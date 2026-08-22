import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_enrollment, require_role
from app.crud import attempt as attempt_crud
from app.crud import content_item as content_item_crud
from app.crud import photocase as photocase_crud
from app.crud import progress as progress_crud
from app.db.session import get_db
from app.models.content_item import ContentItemType
from app.models.user import User, UserRole
from app.schemas.photocase import (
    PhotocaseOptionAdmin,
    PhotocaseOptionCreate,
    PhotocaseOptionUpdate,
    PhotocaseSubmitRequest,
    PhotocaseSubmitResult,
)

router = APIRouter(tags=["photocase"])


@router.post(
    "/content-items/{item_id}/photocase-options",
    response_model=PhotocaseOptionAdmin,
    status_code=status.HTTP_201_CREATED,
)
async def create_photocase_option(
    item_id: uuid.UUID,
    payload: PhotocaseOptionCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    option = await photocase_crud.create_option(
        db,
        content_item_id=item_id,
        label=payload.label,
        is_correct=payload.is_correct,
        explanation=payload.explanation,
        order_index=payload.order_index,
    )
    return PhotocaseOptionAdmin.model_validate(option)


@router.patch("/photocase-options/{option_id}", response_model=PhotocaseOptionAdmin)
async def update_photocase_option(
    option_id: uuid.UUID,
    payload: PhotocaseOptionUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    option = await photocase_crud.get_by_id(db, option_id)
    if option is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вариант не найден")

    option = await photocase_crud.update_option(
        db,
        option,
        label=payload.label,
        is_correct=payload.is_correct,
        explanation=payload.explanation,
        order_index=payload.order_index,
    )
    return PhotocaseOptionAdmin.model_validate(option)


@router.delete("/photocase-options/{option_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photocase_option(
    option_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    option = await photocase_crud.get_by_id(db, option_id)
    if option is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вариант не найден")
    await photocase_crud.delete_option(db, option)


@router.post("/content-items/{item_id}/photocase/submit", response_model=PhotocaseSubmitResult)
async def submit_photocase(
    item_id: uuid.UUID,
    payload: PhotocaseSubmitRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_enrollment),
):
    item = await content_item_crud.get_by_id(db, item_id)
    if item is None or item.type != ContentItemType.photocase:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Фотокейс не найден")

    selected = next((o for o in item.photocase_options if o.id == payload.selected_option_id), None)
    if selected is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Вариант ответа не относится к этому кейсу")

    await attempt_crud.record_photocase_attempt(
        db,
        user_id=user.id,
        content_item_id=item_id,
        selected_option_id=selected.id,
        is_correct=selected.is_correct,
    )
    await progress_crud.mark_completed(db, user_id=user.id, content_item_id=item_id)

    return PhotocaseSubmitResult(
        is_correct=selected.is_correct,
        selected_option_id=selected.id,
        key_signs=item.key_signs,
        next_steps=item.next_steps,
        options=[PhotocaseOptionAdmin.model_validate(o) for o in item.photocase_options],
    )
