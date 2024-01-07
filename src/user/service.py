import os

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import and_
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from ..auth.service import get_hashed_password, verify_password


from ..shared.constants import RoleTypes
from . import utils
from .constants import UserStatus
from .models import Users
from .schemas import UpdateUser, UpdateUserPassword


async def get_user_details(
    user_id: int,
    session: AsyncSession,
):
    # query_result: Result = await session.execute(
    #     select(Users)
    #     .outerjoin(UserAvatar)
    #     .options(joinedload(Users.avatar))
    #     .where(Users.id == user_id)
    # )
    # user = query_result.scalars().first()
    # return user
    return []

async def get_all_users(
    role_id: RoleTypes,
    user_status: UserStatus,
    session: AsyncSession,
):
    # role_list = [role.value for role in RoleTypes]
    # if role_id and role_id not in role_list:
    #     raise HTTPException(
    #         status.HTTP_404_NOT_FOUND,
    #         detail="Invalid RoleID.",
    #     )
    #
    # query = (
    #     select(Users)
    #     .outerjoin(UserAvatar)
    #     .options(joinedload(Users.avatar))
    #     .order_by(Users.id)
    # )
    #
    # if role_id:
    #     query = query.where(Users.role_id == role_id)
    #
    # if user_status:
    #     query = query.where(Users.status == user_status)
    #
    # query_results = await session.execute(query)
    # user_list = query_results.scalars().fetchall()
    # return user_list
    return []

async def update_user_profile(
    user_id: int | None,
    current_user: Users,
    data: UpdateUser,
    session: AsyncSession,
):
    # TODO: fix permission of users
    if current_user.role_id != RoleTypes.Admin.value:
        if user_id and current_user.id != user_id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="The current user can not update another user profile.",
            )
        user_id = current_user.id

    query_result: Result = await session.execute(
        select(Users).where(Users.id == user_id)
    )
    user: Users = query_result.scalars().first()

    if not user:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Invalid UserID.",
        )

    # TODO: Validation for real phone_number
    if user.phone_number != data.phone_number:
        query_result: Result = await session.execute(
            select(Users).where(Users.phone_number == data.phone_number)
        )
        duplicate_phone_number: Users = query_result.scalars().first()

        if duplicate_phone_number:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail=f"User with the phone_number {data.phone_number!r} already exists.",
            )

    if data.middle_name:
        user.middle_name = data.middle_name

    user.first_name = data.first_name
    user.last_name = data.last_name
    user.phone_number = data.phone_number

    await session.commit()


async def change_user_status(
    user_id: int,
    user_status: UserStatus,
    session: AsyncSession,
):
    query_result: Result = await session.execute(
        select(Users).where(Users.id == user_id)
    )
    user: Users = query_result.scalars().first()

    if not user:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Invalid UserID.",
        )

    user.status = user_status

    await session.commit()


async def update_user_password(
    user_id: int,
    update_password: UpdateUserPassword,
    transporter_id: int,
    session: AsyncSession,
):
    users_query_result: Result = await session.execute(
        select(Users).where(Users.id == user_id)
    )
    user: Users = users_query_result.scalars().first()

    if user is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Invalid user id.",
        )

    if not verify_password(update_password.old_password, user.password_hash):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="The old password you have sent is not correct. Please try again.",
        )

    if update_password.new_password != update_password.confirm_new_password:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="The new password and its confirmation do not match. Please try again.",
        )

    user.password_hash = get_hashed_password(update_password.new_password)

    await session.commit()
