import asyncio

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IllegalStateChangeError
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, async_sessionmaker
from sqlalchemy.orm import scoped_session, sessionmaker


async def test_show_same_pid(test_engine):
    """ 순서대로 요청이 오는 경우에는 안전하게 동일한 session을 사용합니다.
    :param test_engine:
    :return:
    """
    session_factory = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    AsyncScopedSession = scoped_session(session_factory)

    async def call0_function():
        await asyncio.sleep(0.1)
        async with AsyncScopedSession() as session:
            result = await session.execute(text("SELECT pg_backend_pid()"))
            return result.scalar()

    async def call1_function():
        async with AsyncScopedSession() as session:
            result = await session.execute(text("SELECT pg_backend_pid()"))
            return result.scalar()

    task1 = asyncio.create_task(call0_function())
    task2 = asyncio.create_task(call1_function())

    output0, output1 = await asyncio.gather(task1, task2)
    assert output0 == output1


async def test_sideeffect_when_rollback_happens(test_engine):
    """ thread가 동일한 session을 사용하는 경우, 다른 쪽에서의 rollback이 정상적으로 처리하는 normal_function에 영향을 미칠 수 있습니다.
    :param test_engine:
    :return:
    """
    session_factory = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    AsyncScopedSession = scoped_session(session_factory)

    async def normal_function():
        async with AsyncScopedSession() as session:
            await session.execute(text("SELECT 1;"))

    async def rollback_function():
        async with AsyncScopedSession() as session:
            await session.rollback()

    task1 = asyncio.create_task(normal_function())
    task2 = asyncio.create_task(rollback_function())

    with pytest.raises(IllegalStateChangeError):
        # rollback에 의해, illegal state change error가 발생합니다.
        await asyncio.gather(task1, task2)


async def test_async_scoped_session(test_engine):
    """ 동시에 요청이 왔을 경우, 서로 다른 session을 사용합니다.
    :param test_engine:
    :return:
    """
    async_session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    AsyncScopedSession = async_scoped_session(async_session_factory, scopefunc=asyncio.current_task)

    async def call_function():
        async with AsyncScopedSession() as session:
            result = await session.execute(text("SELECT pg_backend_pid()"))
            return result.scalar()


    task1 = asyncio.create_task(call_function())
    task2 = asyncio.create_task(call_function())

    output0, output1 = await asyncio.gather(task1, task2)

    assert output0 != output1
