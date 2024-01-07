# business logic
# This is a core of each module with all the endpoints


from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from pydantic import ValidationError
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.database import get_session
from .constants import RoleTypes
from .models import Users

from passlib.context import CryptContext

from datetime import timedelta
from typing import Union, Any
from jose import jwt

from decouple import config

from . import timeutils

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 365  # 365 days
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 365  # 365 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = config('JWT_SECRET_KEY')  # should be kept secret
JWT_REFRESH_SECRET_KEY = config(
    'JWT_REFRESH_SECRET_KEY')  # should be kept secret

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def create_access_token(subject: Union[str, Any],
                        expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = timeutils.now() + expires_delta
    else:
        expires_delta = timeutils.now() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any],
                         expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = timeutils.now() + expires_delta
    else:
        expires_delta = timeutils.now() + timedelta(
            minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt



reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/api/login",
    scheme_name="JWT"
)


async def get_current_user(token: str = Depends(reuseable_oauth),
                           session: AsyncSession = Depends(
                               get_session)) -> Users:
    try:
        payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )

        sub: str = payload["sub"]
        exp: int = payload["exp"]

        if timeutils.fromtimestamp(exp) < timeutils.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except(jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    query_results: Result = await session.execute(
        select(Users).where(Users.username == sub))
    found_user: Users = query_results.scalars().first()

    if not found_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return found_user


async def get_only_superadmin(user: Users = Depends(get_current_user)):
    if user.role_id != RoleTypes.Admin.value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only superadmin can do this",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


