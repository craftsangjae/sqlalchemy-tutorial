import time

import pytest
import logging
import subprocess

from src.models import Base
from sqlalchemy.ext.asyncio import create_async_engine


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


@pytest.fixture(scope="session")
async def build_table(launch_test_db):
    engine = create_async_engine(
        'postgresql+asyncpg://user:password@localhost:5432/testdb',
        echo=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
async def test_engine(build_table):
    yield create_async_engine('postgresql+asyncpg://user:password@localhost:5432/testdb', echo=True)