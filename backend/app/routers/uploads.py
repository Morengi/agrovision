from fastapi import APIRouter, Depends, UploadFile

from app.core.dependencies import require_role
from app.core.uploads import save_image, save_video
from app.models.user import User, UserRole

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/image")
async def upload_editor_image(
    file: UploadFile,
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
) -> dict[str, str]:
    url = await save_image(file, subdir="editor")
    return {"url": url}


@router.post("/video")
async def upload_editor_video(
    file: UploadFile,
    _user: User = Depends(require_role(UserRole.moderator, UserRole.admin)),
) -> dict[str, str]:
    url = await save_video(file, subdir="editor")
    return {"url": url}
