import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, async_scoped_session
from sqlalchemy import inspect

from src.models import UserEntity
import logging


async def test_add_journey(test_engine, with_tables):
    """ add -> flush -> commit -> refresh 순으로 호출

    실제로 entity의 상태가 어떻게 변하는지 확인
    :param test_engine:
    :return:
    """
    async_session_factory = async_sessionmaker(test_engine)
    session_factory = async_scoped_session(async_session_factory, scopefunc=asyncio.current_task)

    logging.info("\ninitialize >>>")
    given_user0 = UserEntity(id=None, name="test0")
    show_entity_status(given_user0)

    async with session_factory() as session:
        logging.info("\nadd >>>")
        session.add(given_user0)
        show_entity_status(given_user0)

        logging.info("\nflush >>>")
        await session.flush([given_user0])
        show_entity_status(given_user0)

        logging.info("\ncommit >>>")
        await session.commit()
        show_entity_status(given_user0)

        logging.info("\nrefresh >>>")
        await session.refresh(given_user0)
        show_entity_status(given_user0)

        logging.info("\nout >>>")
    logging.info("\nclosed >>>")
    show_entity_status(given_user0)


def show_entity_status(entity):
    inspector = inspect(entity)
    logging.info(f"- Transient:{inspector.transient}")
    logging.info(f"- Pending:{inspector.pending}")
    logging.info(f"- Persistent:{inspector.persistent}")
    logging.info(f"- Expired:{inspector.expired}")
    logging.info(f"- Detached:{inspector.detached}")





