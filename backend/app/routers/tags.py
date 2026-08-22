from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_role
from app.crud import tag as tag_crud
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.tag import TagCreate, TagRead

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagRead])
async def list_tags(db: AsyncSession = Depends(get_db)):
    return await tag_crud.list_tags(db)


@router.post("", response_model=TagRead, status_code=201)
async def create_tag(
    payload: TagCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
):
    return await tag_crud.create_tag(db, payload.name)
