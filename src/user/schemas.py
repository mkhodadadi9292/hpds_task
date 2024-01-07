from pydantic import BaseModel

from ..shared.schemas import UserInfo


class UpdateUser(BaseModel):
    first_name: str
    middle_name: str | None
    last_name: str
    phone_number: str


class UpdateUserPassword(BaseModel):
    old_password: str
    new_password: str
    confirm_new_password: str


class SimpleResponse(BaseModel):
    ok: bool


class ErrorSegment(BaseModel):
    code: int
    message: str
