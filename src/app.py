import sys
from typing import List

from fastapi import FastAPI
from sqlalchemy.orm import selectinload

from src.database import Database
from sqlalchemy import select

from src.models import UserEntity
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)

app = FastAPI()
database = Database()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/users/{user_id}")
async def read_user(user_id:int):
    async with database.session() as session:
        connection = await session.connection()
        raw_conn = await connection.get_raw_connection()
        logger.info(f"database connection pool: {id(raw_conn.connection)}")
        stmt = select(UserEntity).where(UserEntity.id == user_id)
        result = await session.execute(stmt)
        user = result.scalars().one_or_none()
        if user:
            return {"user_id": user.id, "name": user.name}
    return {"user_id": user_id}


@app.get("/users")
async def read_users():
    async with database.session() as session:
        stmt = select(UserEntity).options(selectinload(UserEntity.posts))
        result = await session.execute(stmt)
        user_entities: List[UserEntity] = result.scalars().all()
        return [user.to_domain() for user in user_entities]