from pydantic import EmailStr, AnyHttpUrl, BaseModel, StrictInt, Field
from application.enumeration.UserSexEnum import UserSexEnum
from application.initial.BaseEntity import BaseOutEntity
from typing import Optional


class UserBase(BaseModel):
    """
    用户实体类 - 基类
    """
    email: Optional[EmailStr] = None
    phone: Optional[StrictInt] = None


class UserAdd(UserBase):
    """
    用户新增实体类
    """
    nickname: str = Field(max_length=8, min_length=2)
    password: str = Field(min_length=6)
    captcha: Optional[str] = Field(default="xxxxxx", max_length=6, min_length=6, description="邮箱/手机验证码")


class UserLogin(BaseModel):
    """
    用户登陆实体类
    """
    username: str = Field(max_length=32, min_length=4, description="用户名/邮箱/手机号")
    password: Optional[str] = Field(min_length=6)
    captcha: Optional[str] = Field(default="xxxxxx", max_length=6, min_length=6, description="邮箱/手机验证码")
    login_type: str = Field(default="username", description="登陆方式，username/email/phone")


class UserOut(BaseOutEntity, UserBase):
    """
    用户输出实体类
    """
    username: str = Field(max_length=16, min_length=4, default="xxxx")
    nickname: str = Field(max_length=8, min_length=2, default="xxxx")
    age: StrictInt = 18
    avatar: AnyHttpUrl = "https://c-ssl.duitang.com/uploads/blog/202206/12/20220612164733_72d8b.jpg"
    sex: str = UserSexEnum.OTHER.value
    describe: Optional[str] = "简短介绍一下自己吧~"
    occupation: Optional[str] = "未知"
    address: Optional[str] = "未知"
    follow_ids: Optional[str] = "1,2,3"
    fans_ids: Optional[str] = "1,2,3"
    is_disabled: bool = False


class UserSearchOut(BaseOutEntity, BaseModel):
    """
    搜索用户时的实体类
    """
    avatar: AnyHttpUrl = "https://c-ssl.duitang.com/uploads/blog/202206/12/20220612164733_72d8b.jpg"
    username: str = Field(max_length=16, min_length=4, default="xxxx")
    nickname: str = Field(max_length=8, min_length=2, default="xxxx")
    sex: str = UserSexEnum.OTHER.value
    address: Optional[str] = "未知"
    follow_num: int = 0  # 关注数
    fans_num: int = 0  # 粉丝数
