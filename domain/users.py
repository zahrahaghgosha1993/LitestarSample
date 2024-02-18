from advanced_alchemy.base import UUIDBase
from sqlalchemy.orm import Mapped


class User(UUIDBase):
    username: Mapped[str]
    # passwrd : Mapped[password]
