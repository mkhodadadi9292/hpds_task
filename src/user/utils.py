import mimetypes
import os
from uuid import uuid4

from decouple import config

from .constants import AvatarType


async def get_file_name(file_type: str):
    return f"{uuid4()}.{file_type}"


async def get_file_path():
    avatar_dir = config("AVATAR_DIR")
    return avatar_dir


async def get_file_full_path(file_path: str, file_name: str):
    return os.path.join(file_path, file_name)


async def get_file_type(file_name: str):
    allowed_type = [avatar_type.value for avatar_type in AvatarType]
    file_type, encoding = mimetypes.guess_type(file_name)
    file_type = file_type.split("/")[-1]
    if file_type not in allowed_type:
        return None
    return file_type


async def get_file_size(file_name: str):
    return os.path.getsize(file_name)
