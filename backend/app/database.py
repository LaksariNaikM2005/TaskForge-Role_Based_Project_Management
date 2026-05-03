from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.config import settings


class Base(DeclarativeBase):
    pass


def get_engine():
    url = settings.async_database_url
    connect_args = {}
    if "sqlite" in url:
        connect_args = {"check_same_thread": False}
    return create_async_engine(url, echo=False, connect_args=connect_args)


engine = get_engine()
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
