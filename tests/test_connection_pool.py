import time

import pytest
import sqlalchemy
from sqlalchemy import text
import logging

from sqlalchemy.ext.asyncio import create_async_engine


async def test_measure_elapsed_time_per_step_with_connection_pool(test_engine):
    """
    왜 커넥션 풀이 필요할까요?

    => 커넥션을 맺는 과정은 생각보다 비쌉니다.
    - TCP/IP 연결을 맺는 과정
    - 인증 과정
    - 세션 설정 (ex. timezone 설정, character set 설정, resource 할당 등)
    - 데이터베이스 정보 조회 (ex. 데이터베이스 버전 조회)

    => `select 1` 쿼리를 날리는 동작에서 각 단계 별로 걸리는 시간을 측정해보면,
    select 1 쿼리를 날리고 응답을 받는 시간보다, 커넥션을 맺는 시간이 더 오래 걸립니다.

    => 이미 맺은 커넥션을 바로 해제하지 않고 재사용함으로써, 이 비용을 줄일 수 있습니다.
    이러한 메커니즘을 커넥션 풀이라고 합니다.

    :return:
    """
    query = text("SELECT 1")

    start_time = time.perf_counter()
    async with test_engine.connect() as conn:
        elapsed_time = time.perf_counter() - start_time
        logging.info(f"(1) 데이터베이스 연결에 걸린 시간: {elapsed_time:.4f}초")

        start_time = time.perf_counter()
        await conn.execute(query)
        elapsed_time = time.perf_counter() - start_time
        logging.info(f"(2) select query 날리는데 걸린 시간: {elapsed_time:.4f}초")

        start_time = time.perf_counter()
    elapsed_time = time.perf_counter() - start_time
    logging.info(f"(3) 데이터베이스 연결 해제에 걸린 시간: {elapsed_time:.4f}초")

    start_time = time.perf_counter()
    async with test_engine.connect() as conn:
        elapsed_time = time.perf_counter() - start_time
        logging.info(f"(4) 다시 데이터베이스 연결에 걸린 시간: {elapsed_time:.4f}초")

        start_time = time.perf_counter()
        await conn.execute(query)
        elapsed_time = time.perf_counter() - start_time
        logging.info(f"(5) select query 날리는데 걸린 시간: {elapsed_time:.4f}초")


async def test_measure_elapsed_time_per_step_with_pool_recycle(test_engine):
    """
    pool_recycle 옵션은 커넥션을 재사용하기 전에 커넥션을 재생성하는 주기를 설정합니다.
    커넥션이 오래되어 있으면 오류가 발생할 수 있기 때문에, 이 옵션을 사용하여 커넥션을 주기적으로 재생성합니다.

    :return:
    """
    test_engine = create_async_engine(
        'postgresql+asyncpg://user:password@localhost:5432/testdb',
        echo=True,
        pool_recycle=1
    )

    query = text("SELECT 1")

    start_time = time.perf_counter()
    async with test_engine.connect() as conn:
        elapsed_time = time.perf_counter() - start_time
        logging.info(f"(1) 데이터베이스 연결에 걸린 시간: {elapsed_time:.4f}초")

        start_time = time.perf_counter()
        await conn.execute(query)
        elapsed_time = time.perf_counter() - start_time
        logging.info(f"(2) select query 날리는데 걸린 시간: {elapsed_time:.4f}초")

        start_time = time.perf_counter()
    elapsed_time = time.perf_counter() - start_time
    logging.info(f"(3) 데이터베이스 연결 해제에 걸린 시간: {elapsed_time:.4f}초")

    time.sleep(2)

    start_time = time.perf_counter()
    async with test_engine.connect() as conn:
        elapsed_time = time.perf_counter() - start_time
        logging.info(f"(4) 다시 데이터베이스 연결에 걸린 시간: {elapsed_time:.4f}초")

        start_time = time.perf_counter()
        await conn.execute(query)
        elapsed_time = time.perf_counter() - start_time
        logging.info(f"(5) select query 날리는데 걸린 시간: {elapsed_time:.4f}초")


async def test_exceed_connection_pool(test_engine):
    """
    pool size가 넘어가면, 커넥션을 새로 맺지 않고 기다리게 됩니다.
    이 때, 기다리는 시간은 pool timeout으로 결정됩니다.

    :return:
    """
    test_engine = create_async_engine(
        'postgresql+asyncpg://user:password@localhost:5432/testdb',
        echo=True,
        pool_size=10,
        max_overflow=0,
        pool_timeout=1,
    )

    conns = []
    for _ in range(10):
        conns.append(await test_engine.connect())
    logging.info(conns)

    with pytest.raises(sqlalchemy.exc.TimeoutError):
        await test_engine.connect()


async def test_set_statement_timeout(test_engine):
    """
    asyncpg의 command_timeout 옵션을 사용하여 statement timeout을 설정할 수 있습니다.
    * https://magicstack.github.io/asyncpg/current/api/index.html

    => 지나치게 오래걸리는 query로 인해 서비스가 장애나는 것을 방지하기 위함입니다.

    :return:
    """
    # 1초 statement timeout을 설정합니다.
    test_engine = create_async_engine(
        'postgresql+asyncpg://user:password@localhost:5432/testdb',
        echo=True,
        connect_args={"server_settings": {"statement_timeout": "1000"}}
    )

    async with test_engine.connect() as conn:

        with pytest.raises(sqlalchemy.exc.StatementError):
            # 1초가 넘어가면 에러가 발생합니다.
            await conn.execute(text("SELECT pg_sleep(1.1)"))


