from pydantic import EmailStr, AnyHttpUrl, BaseModel, StrictInt, Field
from application.enumeration.UserSexEnum import UserSexEnum
from application.entity import BaseOutEntity
from typing import Optional


class UserBase(BaseModel):
    """
    用户实体类 - 基类
    """
    nickname: str = Field(max_length=8, min_length=2)
    email: Optional[EmailStr] = None
    phone: Optional[StrictInt] = None


class UserAdd(UserBase):
    """
    用户新增实体类
    """
    password: str


class UserOut(BaseOutEntity, UserBase):
    """
    用户输出实体类
    """
    username: Optional[str] = None
    age: StrictInt = 18
    avatar: AnyHttpUrl = "https://c-ssl.duitang.com/uploads/blog/202206/12/20220612164733_72d8b.jpg"
    sex: str = UserSexEnum.OTHER.value
    describe: Optional[str] = "简短介绍一下自己吧~"
    occupation: Optional[str] = "未知"
    address: Optional[str] = "未知"
    follow_ids: Optional[str] = None
    fans_ids: Optional[str] = None
    is_disabled: bool = False
