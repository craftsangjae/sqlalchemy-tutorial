from typing import List

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domains import User, Post


class Base(AsyncAttrs, DeclarativeBase):
    pass


class PostEntity(Base):
    __tablename__ = 'posts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped['UserEntity'] = relationship(back_populates="posts")

    @staticmethod
    def from_domain(post: Post):
        return PostEntity(id=post.id, user_id=post.user_id, title=post.title)


class UserEntity(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    posts: Mapped[List[PostEntity]] = relationship(back_populates="user")

    @staticmethod
    def from_domain(user: User):
        return UserEntity(id=user.id, name=user.name)
