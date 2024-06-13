from application.entity import BaseEntity
from typing import Optional


class UserBase(BaseEntity):
    """
    用户实体类 - 基类
    """
    username: str
    nickname: str
    email: Optional[str]
    avatar: Optional[str]
    is_active: Optional[bool]


class UserIn(UserBase):
    """
    用户输入实体类
    """
    password: str


class UserOut(UserBase):
    """
    用户输出实体类
    """
    pass
