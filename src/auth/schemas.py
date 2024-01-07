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


class UserInfo(BaseModel):
    first_name: str
    last_name: str
    username: str
    created_at: datetime
    role_id: int

    class Config:
        from_attributes = True
