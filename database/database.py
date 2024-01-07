from . import config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(config.DATABASE_URL, future=True, echo=True)
async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def create_all():
    from database.base import Base
    from src.auth.models import Base
    from src.memory_managment.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
        await session.commit()


async def create_admin_user():
    # Username and password can be changed by the config file.
    # Admin can only start memory manager.
    from src.auth.models import Users
    from src.auth.service import get_hashed_password
    from src.auth.schemas import RoleTypes

    async with async_session_maker() as session:
        admin = Users(first_name="admin",
                      last_name="admin",
                      phone_number="123",
                      username=config.ADMIN_USERNAME,
                      password_hash=get_hashed_password(config.ADMIN_PASSWORD),
                      role_id=RoleTypes.Admin.value)
        session.add(admin)
        await session.commit()


async def add_default_roles():
    from src.auth.models import Roles
    from src.auth.schemas import RoleTypes
    async with async_session_maker() as session:
        admin_role = Roles(id=RoleTypes.Admin.value,
                           name=RoleTypes.Admin.name)
        regular_role = Roles(id=RoleTypes.Regular.value,
                             name=RoleTypes.Regular.name)

        session.add_all([admin_role, regular_role])
        await session.commit()
