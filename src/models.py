from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from src.domains import User

Base = declarative_base()


class UserEntity(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    @staticmethod
    def from_domain(user: User):
        return UserEntity(name=user.name)
