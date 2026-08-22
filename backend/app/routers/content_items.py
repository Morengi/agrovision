import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_role
from app.core.uploads import delete_image_file, save_image
from app.crud import content_item as content_item_crud
from app.crud import content_item_image as image_crud
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.content_item import (
    ContentItemAdminDetail,
    ContentItemCreate,
    ContentItemDetail,
    ContentItemImageRead,
    ContentItemSummary,
    ContentItemUpdate,
)

router = APIRouter(tags=["content-items"])


@router.get("/topics/{topic_id}/content-items", response_model=list[ContentItemSummary])
async def list_content_items(topic_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    items = await content_item_crud.list_by_topic(db, topic_id)
    return [ContentItemSummary.model_validate(i) for i in items]


@router.get("/content-items/{item_id}", response_model=ContentItemDetail)
async def get_content_item(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    item = await content_item_crud.get_by_id(db, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Материал не найден")
    return ContentItemDetail.model_validate(item)


@router.get("/content-items/{item_id}/admin", response_model=ContentItemAdminDetail)
async def get_content_item_admin(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    item = await content_item_crud.get_by_id(db, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Материал не найден")
    return ContentItemAdminDetail.model_validate(item)


@router.post(
    "/topics/{topic_id}/content-items", response_model=ContentItemAdminDetail, status_code=status.HTTP_201_CREATED
)
async def create_content_item(
    topic_id: uuid.UUID,
    payload: ContentItemCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    item = await content_item_crud.create_content_item(
        db,
        topic_id=topic_id,
        type=payload.type,
        title=payload.title,
        order_index=payload.order_index,
        text_body=payload.text_body,
    )
    return ContentItemAdminDetail.model_validate(item)


@router.patch("/content-items/{item_id}", response_model=ContentItemAdminDetail)
async def update_content_item(
    item_id: uuid.UUID,
    payload: ContentItemUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    item = await content_item_crud.get_by_id(db, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Материал не найден")

    item = await content_item_crud.update_content_item(
        db,
        item,
        title=payload.title,
        order_index=payload.order_index,
        text_body=payload.text_body,
        key_signs=payload.key_signs,
        next_steps=payload.next_steps,
    )
    return ContentItemAdminDetail.model_validate(item)


@router.delete("/content-items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content_item(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    item = await content_item_crud.get_by_id(db, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Материал не найден")
    await content_item_crud.delete_content_item(db, item)


@router.post("/content-items/{item_id}/images", response_model=list[ContentItemImageRead])
async def upload_content_item_images(
    item_id: uuid.UUID,
    files: list[UploadFile],
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    item = await content_item_crud.get_by_id(db, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Материал не найден")

    for file in files:
        image_path = await save_image(file, subdir=str(item_id))
        await image_crud.add_image(db, content_item_id=item_id, image_path=image_path)

    await db.refresh(item, attribute_names=["images"])
    return [ContentItemImageRead.model_validate(i) for i in item.images]


@router.delete("/content-item-images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content_item_image(
    image_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    image = await image_crud.get_by_id(db, image_id)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Изображение не найдено")
    delete_image_file(image.image_path)
    await image_crud.delete_image(db, image)
