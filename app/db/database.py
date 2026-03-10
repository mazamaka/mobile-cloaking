"""Async database engine and session management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from config import SETTINGS


class Database:
    """Async database wrapper with session management.

    Uses NullPool for serverless-friendly connection handling.
    Sessions auto-commit on success and rollback on exception.
    """

    def __init__(self, url: str, *, echo: bool = False) -> None:
        self.engine = create_async_engine(
            url,
            echo=echo,
            poolclass=NullPool,
        )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    async def create_tables(self) -> None:
        """Create all tables from SQLModel metadata."""
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def drop_tables(self) -> None:
        """Drop all tables from SQLModel metadata."""
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Context manager for database session with auto-commit/rollback."""
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """FastAPI dependency yielding a database session."""
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def close(self) -> None:
        """Dispose of the database engine and release connections."""
        await self.engine.dispose()


db = Database(url=SETTINGS.database_url, echo=SETTINGS.debug)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database session injection."""
    async for session in db.get_session():
        yield session
