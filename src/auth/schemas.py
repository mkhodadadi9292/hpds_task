from datetime import datetime, time, date
from typing import Any, List, Optional
from pydantic import BaseModel, Field, field_validator, Json
from .constants import RoleTypes


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class Body(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    username: str
    password: str


class SimpleResponse(BaseModel):
    ok: bool


class ErrorSegment(BaseModel):
    code: int
    message: str


####################################################################################################
class UserSignupRequest(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    email: str
    username: str = Field(..., description="new user's username")
    password: str = Field(..., min_length=8, max_length=24, description="new user's password")
    role_id: int = Field(..., description="the integer of role")

    @field_validator('role_id', mode="after")
    def role_must_be_valid(cls, role):
        for eachRole in RoleTypes:
            if role == eachRole.value:
                return role
        raise ValueError('role must be a valid int from predefined enum')


####################################################################################################
class UserInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone_number: str
    email: str
    username: str
    created_at: datetime
    role_id: int

    class Config:
        from_attributes = True
