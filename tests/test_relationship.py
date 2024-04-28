from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models import UserEntity, PostEntity
import logging


async def test_select_with_relationship(test_scoped_session):
    """
    """
    # given case
    async with test_scoped_session() as session:
        entity = UserEntity(id=None, name="test0")
        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        user0_id = entity.id

        session.add(PostEntity(id=None, user_id=user0_id, title="title0"))
        session.add(PostEntity(id=None, user_id=user0_id, title="title1"))
        session.add(PostEntity(id=None, user_id=user0_id, title="title2"))
        await session.commit()

        entity = UserEntity(id=None, name="test1")
        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        user1_id = entity.id

        session.add(PostEntity(id=None, user_id=user1_id, title="title3"))
        session.add(PostEntity(id=None, user_id=user1_id, title="title4"))
        session.add(PostEntity(id=None, user_id=user1_id, title="title5"))
        await session.commit()

    logging.info("\nwithout eager loading >>>")
    async with test_scoped_session() as session:
        logging.info("\ncreate stmt >>>")
        stmt = select(UserEntity)
        logging.info("\nsession execute >>>")
        result = await session.execute(stmt)
        user_entities = result.scalars().all()

        logging.info("\nget post >>>")
        for user_entity in user_entities:
            logging.info(f"\n  -get post(user_id:{user_entity.id}) >>>")
            post_entities = await user_entity.awaitable_attrs.posts

    logging.info("\nwith eager loading >>>")
    async with test_scoped_session() as session:
        logging.info("\ncreate stmt >>>")
        stmt = select(UserEntity).options(selectinload(UserEntity.posts))
        logging.info("\nsession execute >>>")
        result = await session.execute(stmt)
        user_entities = result.scalars().all()

        logging.info("\nget posts >>>")
        for user_entity in user_entities:
            logging.info(f"\n  -get post(user_id:{user_entity.id}) >>>")
            post_entities = user_entity.posts





