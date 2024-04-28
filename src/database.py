"""Database module."""
import asyncio
import logging
from contextlib import AbstractContextManager, asynccontextmanager
from typing import Callable

from sqlalchemy.ext.asyncio import async_sessionmaker, async_scoped_session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from src.models import Base

logger = logging.getLogger(__name__)


class Database:
    """비동기 데이터베이스 클래스"""

    def __init__(self):
        self._engine = create_async_engine("postgresql+asyncpg://user:password@localhost:5432/testdb", echo=True)

        self._session_factory = async_scoped_session(
            async_sessionmaker(
                autocommit=False,
                bind=self._engine,
            ),
            scopefunc=asyncio.current_task,
        )

    async def create_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_database(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @asynccontextmanager
    async def session(self) -> Callable[[], AbstractContextManager[AsyncSession]]:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception as e:
            logger.exception("Session rollback because of exception")
            await session.rollback()
            raise e
        finally:
            await session.close()
            await self._session_factory.remove()

