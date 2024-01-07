from typing import List

from database.database import get_session
from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth.dependencies import get_current_user, get_only_superadmin
from . import service
from .constants import UserStatus
from .models import Users
from .schemas import UpdateUser, UpdateUserPassword
from .service import get_all_users, update_user_profile
from .schemas import UserInfo

router = APIRouter(prefix="/user", tags=["User"])



@router.get(
    "/details",
    summary="Get User Details",
    status_code=status.HTTP_200_OK,
    response_model=UserInfo,
)
async def user_details(
    session: AsyncSession = Depends(get_session),
    authorize: Users = Depends(get_current_user),
):
    user = await service.get_user_details(authorize.id, session)
    return user


@router.get(
    "/all",
    summary="Get All Users",
    status_code=status.HTTP_200_OK,
    response_model=List[UserInfo],
)
async def all_users(
    role_id: int = None,
    user_status: UserStatus = None,
    session: AsyncSession = Depends(get_session),
    authorize: Users = Depends(get_only_superadmin),
):
    user_list = await get_all_users(role_id, user_status, session)
    return user_list


@router.put(
    "/profile",
    summary="Update User Profile",
    status_code=status.HTTP_200_OK,
)
async def update_user(
    data: UpdateUser,
    user_id: int = None,
    session: AsyncSession = Depends(get_session),
    authorize: Users = Depends(get_current_user),
):
    return await update_user_profile(user_id, authorize, data, session)



@router.patch(
    "/password/{user_id}",
    summary="Update User Password",
    status_code=status.HTTP_200_OK
)
async def update_user_password(
    user_id: int,
    update_password: UpdateUserPassword,
    session: AsyncSession = Depends(get_session)
):
    await service.update_user_password(user_id, update_password, authorize.id, session)
