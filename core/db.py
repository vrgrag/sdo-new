from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from core.config import DATABASE_URL_ASYNC
engine = create_async_engine(DATABASE_URL_ASYNC, pool_pre_ping=True)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
Base = declarative_base()

async def get_db() -> AsyncSession:
    async with SessionLocal() as db:
        yield db
