from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: Optional[int]
    name: str

    @staticmethod
    def new(name: str):
        return User(id=None, name=name)