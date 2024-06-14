"""
Token验证相关依赖
"""
from fastapi import Header, Depends
from application.util import TokenUtil
from tortoise.exceptions import DoesNotExist
from application.model.UserModel import UserModel
from application.exception.BasicException import BasicException
from application.enumeration.StatusCodeEnum import StatusCodeEnum


async def verify_token(authorization: str = Header()) -> int:
    """
    验证Token
    :param authorization: 从Header中获取authorization的值
    :return: 用户ID
    """
    user_id: int = TokenUtil.get_user_id(token=authorization)
    if not TokenUtil.verify_token(token=authorization) or user_id == 0:
        raise BasicException(status_code=StatusCodeEnum.AUTHORITY_ERROR.value, message="登陆状态失效！")
    return user_id

async def get_current_user(user_id: int = Depends(verify_token)) -> UserModel:
    """
    获取当前用户
    :param user_id: 用户ID
    :return: 用户ORM模型
    """
    try:
        user_model: UserModel = await UserModel.get(id=user_id)
        return user_model
    except DoesNotExist:
        raise BasicException(status_code=StatusCodeEnum.AUTHORITY_ERROR.value, message="无权限访问！")