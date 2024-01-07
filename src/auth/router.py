from fastapi import APIRouter
from fastapi import status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .dependencies import (
    create_access_token,
    create_refresh_token,
    verify_password,
)
from database.database import get_session
from .models import Users
from .schemas import TokenSchema, SimpleResponse, Body
from .constants import RoleTypes
from .service import get_hashed_password
router = APIRouter(tags=["Authentication"])

@router.post('/register', summary= "create a new User", response_model=SimpleResponse)
async def create_user(body:Body, session: AsyncSession = Depends(get_session)):
    user = Users(first_name=body.first_name,
                 last_name=body.last_name,
                 phone_number=body.phone_number,
                 username=body.username,
                 role=RoleTypes.Regular.value,
                 password_hash=get_hashed_password(body.password))
    session.add(user)
    await session.commit()
    return SimpleResponse
@router.post('/login',
             summary="Create access and refresh tokens for all users",
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
