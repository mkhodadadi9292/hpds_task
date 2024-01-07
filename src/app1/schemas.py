# src/app1/schemas.py

from pydantic import BaseModel


class UserSchema(BaseModel):
    name: str
    email: str
