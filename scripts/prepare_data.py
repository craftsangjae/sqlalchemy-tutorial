import asyncio

from src.database import Database
from src.models import PostEntity, UserEntity


async def main():
    database = Database()
    async with database.session() as session:
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

if __name__ == '__main__':
    asyncio.run(main())