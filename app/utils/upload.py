import os
import shutil
from datetime import datetime
from fastapi import File, UploadFile
from typing import Optional
from app.config.settings import settings
from app.exceptions.custom_exceptions import BadRequestException

ALLOWED_AVATAR_TYPES = {"image/jpeg", "image/png", "image/jpg"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def _validate(file: UploadFile) -> None:
    if file.content_type not in ALLOWED_AVATAR_TYPES:
        raise BadRequestException("Invalid avatar format. Only JPEG and PNG are allowed.")

    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_FILE_SIZE:
        raise BadRequestException("Avatar must be less than 5MB.")


def _save(file: UploadFile) -> str:
    dest_dir = os.path.join(settings.uploads_dir, "avatars")
    os.makedirs(dest_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1]
    filename = f"{datetime.now().timestamp()}{ext}"
    with open(os.path.join(dest_dir, filename), "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return filename


# The multer equivalent — used as Depends(process_avatar) in routes
async def process_avatar(avatar: Optional[UploadFile] = File(None)) -> Optional[str]:
    """
    Dependency that acts like multer.single("avatar").
    If avatar is provided: validates + saves + returns filename string.
    If avatar is not provided: returns None (update profile without changing avatar).
    Controller receives clean Optional[str], never the raw file bytes.
    """
    if not avatar or not avatar.filename:
        return None
    _validate(avatar)
    return _save(avatar)
