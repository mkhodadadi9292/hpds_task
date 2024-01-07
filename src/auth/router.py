from fastapi import status, HTTPException, Depends, APIRouter, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from .dependencies import (
    create_access_token,
    create_refresh_token,
    verify_password,
)
from database.database import get_session, async_session_maker
from .models import Users
from .schemas import TokenSchema, Body, UserInfo
from .constants import RoleTypes
from .dependencies import get_hashed_password

router = APIRouter(tags=["Authentication"])


@router.post('/register', summary="create a new User", status_code=status.HTTP_201_CREATED, response_model=UserInfo)
async def create_user(body: Body, session: AsyncSession = Depends(get_session)):
    try:
        user = Users(first_name=body.first_name,
                     last_name=body.last_name,
                     phone_number=body.phone_number,
                     username=body.username,
                     role_id=RoleTypes.Regular.value,
                     password_hash=get_hashed_password(body.password))
        session.add(user)
        await session.commit()
        return UserInfo(username=user.username,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        role_id=user.role_id,
                        created_at=user.created_at)

    except IntegrityError as e:
        error_message = str(e.orig).lower()
        if 'unique constraint' in error_message:
            custom_error_message = "username or phone number have already existed."
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=custom_error_message)


@router.post('/login',
             summary="Create access and refresh tokens for all users", status_code=status.HTTP_201_CREATED,
             response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                session: AsyncSession = Depends(get_session)):
    print(f"Searching for username: {form_data.username} ...")
    query_results: Result = await session.execute(
        select(Users).where(Users.username == form_data.username))
    found_user: Users = query_results.scalars().first()

    if not found_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )

    hashed_pass = found_user.password_hash
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )

    return TokenSchema(
        access_token=create_access_token(found_user.username),
        refresh_token=create_refresh_token(found_user.username)
    )
