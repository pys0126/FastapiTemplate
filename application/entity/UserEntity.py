from pydantic import EmailStr, AnyHttpUrl, BaseModel, StrictInt
from application.enumeration.UserSexEnum import UserSexEnum
from application.entity import BaseOutEntity
from typing import Optional


class UserBase(BaseModel):
    """
    用户实体类 - 基类
    """
    username: str
    nickname: str
    email: Optional[EmailStr] = None
    phone: Optional[StrictInt] = None
    age: StrictInt = 18
    avatar: AnyHttpUrl = "https://c-ssl.duitang.com/uploads/blog/202206/12/20220612164733_72d8b.jpg"
    sex: str = UserSexEnum.OTHER.value
    is_active: bool = True


class UserIn(UserBase):
    """
    用户输入实体类
    """
    password: str


class UserOut(BaseOutEntity, UserBase):
    """
    用户输出实体类
    """
    pass
