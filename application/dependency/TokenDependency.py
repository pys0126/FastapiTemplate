"""
Token验证相关依赖
"""
from fastapi import Header, Depends
from application.util import TokenUtil
from tortoise.exceptions import DoesNotExist
from application.service.user.Model import UserModel
from application.initial.BaseEnum import StatusCodeEnum
from application.exception.BasicException import BasicException


async def parse_token(authorization: str = Header(default="")) -> int:
    """
    解析Token拿到用户ID（不含验证）
    :param authorization: 从Header中获取authorization的值
    :return: 未知或无Token都为0
    """
    return await TokenUtil.get_user_id(token=authorization)


async def verify_token(authorization: str = Header()) -> int:
    """
    验证Token
    :param authorization: 从Header中获取authorization的值
    :return: 用户ID
    """
    user_id: int = await TokenUtil.get_user_id(token=authorization)
    # 未注册
    if not await UserModel.filter(id=user_id).exists():
        raise BasicException(status_code=StatusCodeEnum.AUTHORITY_ERROR, message="无权限访问！")
    # 登录失效
    if not await TokenUtil.verify_token(token=authorization) or user_id == 0:
        raise BasicException(status_code=StatusCodeEnum.LOGIN_STATUS_EXPIRED, message="登陆状态失效！")
    return user_id


async def get_current_user(user_id: int = Depends(verify_token)) -> UserModel:
    """
    获取当前用户ORM模型（无限制）
    :param user_id: 用户ID
    :return: 用户ORM模型
    """
    try:
        user_model: UserModel = await UserModel.get(id=user_id)
        return user_model
    except DoesNotExist:
        raise BasicException(status_code=StatusCodeEnum.AUTHORITY_ERROR, message="无权限访问！")
