import pytest
import logging
import subprocess

from src.models import Base
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.fixture(scope="session")
def launch_test_db(pytestconfig):
    minio_docker_path = str(pytestconfig.rootpath / "tests/test-posgres-db.yaml")
    logging.info("통합테스트용 S3 Object Storage 테스트 환경 구축을 시작합니다... (minIO 구축)")
    subprocess.run(["docker-compose", "-f", minio_docker_path, "up", "-d"], check=True)
    yield
    subprocess.run(["docker-compose", "-f", minio_docker_path, "down"], check=True)


@pytest.fixture(scope="session")
def test_engine(launch_test_db):
    engine = create_async_engine('postgresql+asyncpg://user:password@localhost:5432/testdb')
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)