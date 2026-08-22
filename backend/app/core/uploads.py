import uuid
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings

settings = get_settings()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
IMAGE_EXTENSION_BY_TYPE = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}

ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/ogg"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".webm", ".ogv", ".ogg"}
VIDEO_EXTENSION_BY_TYPE = {"video/mp4": ".mp4", "video/webm": ".webm", "video/ogg": ".ogv"}


async def _save_file(
    file: UploadFile,
    *,
    kind_dir: str,
    subdir: str,
    allowed_types: set[str],
    allowed_extensions: set[str],
    extension_by_type: dict[str, str],
    max_size_bytes: int,
    error_detail: str,
) -> str:
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=error_detail)

    extension = Path(file.filename or "").suffix.lower()
    if extension not in allowed_extensions:
        extension = extension_by_type.get(file.content_type, next(iter(allowed_extensions)))

    target_dir = Path(settings.media_root) / kind_dir / subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4()}{extension}"
    target_path = target_dir / filename

    size = 0
    async with aiofiles.open(target_path, "wb") as out_file:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > max_size_bytes:
                await out_file.close()
                target_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Файл слишком большой",
                )
            await out_file.write(chunk)

    return f"/media/{kind_dir}/{subdir}/{filename}"


async def save_image(file: UploadFile, *, subdir: str) -> str:
    return await _save_file(
        file,
        kind_dir="images",
        subdir=subdir,
        allowed_types=ALLOWED_IMAGE_TYPES,
        allowed_extensions=ALLOWED_IMAGE_EXTENSIONS,
        extension_by_type=IMAGE_EXTENSION_BY_TYPE,
        max_size_bytes=settings.max_upload_size_bytes,
        error_detail="Поддерживаются только изображения JPEG, PNG и WEBP",
    )


async def save_video(file: UploadFile, *, subdir: str) -> str:
    return await _save_file(
        file,
        kind_dir="videos",
        subdir=subdir,
        allowed_types=ALLOWED_VIDEO_TYPES,
        allowed_extensions=ALLOWED_VIDEO_EXTENSIONS,
        extension_by_type=VIDEO_EXTENSION_BY_TYPE,
        max_size_bytes=settings.max_video_upload_size_bytes,
        error_detail="Поддерживаются только видео MP4, WEBM и OGG",
    )


def delete_image_file(image_path: str) -> None:
    if not image_path.startswith("/media/"):
        return
    relative = image_path.removeprefix("/media/")
    full_path = Path(settings.media_root) / relative
    full_path.unlink(missing_ok=True)
