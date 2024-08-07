from typing import Optional
from application.mapper import BaseMapper
from application.model.UserModel import UserModel


class UserMapper(BaseMapper):
    """
    用户DAO层
    """
    orm_model: UserModel = UserModel

    @classmethod
    async def get_data_by_email(cls, email: str) -> Optional[UserModel]:
        """
        根据邮箱获取用户信息
        :param email: 邮箱
        :return: 用户模型
        """
        return await cls.orm_model.get_or_none(email=email)
    
    @classmethod
    async def get_data_by_username(cls, username: str) -> Optional[UserModel]:
        """
        根据用户名获取用户信息
        :param username: 用户名
        :return: 用户模型
        """
        return await cls.orm_model.get_or_none(username=username)
    
    @classmethod
    async def get_data_by_phone(cls, phone: int) -> Optional[UserModel]:
        """
        根据手机号获取用户信息
        :param phone: 手机号
        :return: 用户模型
        """
        return await cls.orm_model.get_or_none(phone=phone)