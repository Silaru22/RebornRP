from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

async_engine = create_async_engine(
    url=f'postgresql+asyncpg://{settings.teable_db_user}:{settings.teable_db_password.get_secret_value()}@{settings.teable_db_host}:{settings.teable_db_port}/{settings.teable_db_db}',
    echo=False,
    pool_size=5,
    max_overflow=10,
)

async_session_factory = async_sessionmaker(async_engine, autoflush=False, expire_on_commit=False)


@asynccontextmanager
async def session_getter() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        yield session
