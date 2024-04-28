import time

from sqlalchemy import text
import logging


async def test_measure_elapsed_time_per_step_without_connection_pool(test_engine):
    """
    왜 커넥션 풀이 필요할까요?

    => 커넥션을 맺는 과정은 생각보다 비쌉니다.

    => `select 1` 쿼리를 날리는 동작에서 각 단계 별로 걸리는 시간을 측정해보면,
    select 1 쿼리를 날리고 응답을 받는 시간보다, 커넥션을 맺는 시간이 더 오래 걸립니다.

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

