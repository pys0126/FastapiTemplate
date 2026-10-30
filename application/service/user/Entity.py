from application.initial.BaseEntity import BaseOutEntity, BaseInputEntity
from pydantic import AnyHttpUrl, Field
from typing import Optional


class UserAdd(BaseInputEntity):
    """
    用户新增实体类
    """
    username: str = Field(max_length=16, min_length=4, description="用户名")
    nickname: str = Field(max_length=8, min_length=2)
    password: str = Field(min_length=6)
    avatar: Optional[AnyHttpUrl] = Field(default=None, description="头像URL")
    intro: Optional[str] = Field(default=None, max_length=250, description="个人简介")


class UserLogin(BaseInputEntity):
    """
    用户登录实体类
    """
    username: str = Field(max_length=16, min_length=4, description="用户名")
    password: str = Field(min_length=6)


class UserOut(BaseOutEntity):
    """
    用户输出实体类
    """
    username: str
    nickname: str
    avatar: AnyHttpUrl
    intro: str
    is_disabled: bool
