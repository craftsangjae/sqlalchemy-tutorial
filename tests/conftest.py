import asyncio
import time

import pytest
import logging
import subprocess

from src.models import Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, async_scoped_session

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)


@pytest.fixture(scope="session")
def launch_test_db(pytestconfig):
    minio_docker_path = str(pytestconfig.rootpath / "tests/test-posgres-db.yaml")
    logging.info("통합테스트용 postgresql 테스트 환경 구축을 시작합니다")
    subprocess.run(["docker-compose", "-f", minio_docker_path, "up", "-d"], check=True)
    time.sleep(5)
    yield
    subprocess.run(["docker-compose", "-f", minio_docker_path, "down"], check=True)


@pytest.fixture()
async def test_engine(launch_test_db):
    yield create_async_engine('postgresql+asyncpg://user:password@localhost:5432/testdb', echo=True)


@pytest.fixture()
async def with_tables(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture()
async def test_scoped_session(with_tables, test_engine):
    async_session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    yield async_scoped_session(async_session_factory, scopefunc=asyncio.current_task)