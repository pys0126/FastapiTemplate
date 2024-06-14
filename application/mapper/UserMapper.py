from application.mapper import BaseMapper
from application.model.UserModel import UserModel


class UserMapper(BaseMapper):
    """
    用户DAO层
    """
    orm_model: UserModel = UserModel