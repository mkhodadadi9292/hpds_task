import sqlalchemy
# from decouple import config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, future=True, echo=True)
async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


async def create_all():
    from database.database import Base
    from src.auth.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
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
