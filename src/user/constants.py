from enum import Enum


class UserStatus(Enum):
    Active = "Active"
    Inactive = "Inactive"
    Deleted = "Deleted"


class AvatarType(Enum):
    jpg = "jpg"
    jpeg = "jpeg"
    png = "png"
