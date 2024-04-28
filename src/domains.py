from dataclasses import dataclass
from typing import Optional, List


@dataclass
class User:
    id: Optional[int]
    name: str
    posts: List['Post']

    @staticmethod
    def new(name: str):
        return User(id=None, name=name, posts=[])


@dataclass
class Post:
    id: Optional[int]
    user_id: str
    title: str

    @staticmethod
    def new(user_id: str, title: str):
        return Post(id=None, user_id=user_id, title=title)
