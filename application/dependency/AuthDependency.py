"""
Token验证相关依赖
"""
from fastapi import Depends, Header, Request
from tortoise.exceptions import DoesNotExist
from application.exception.BasicException import BasicException
from application.initial.BaseEnum import StatusCodeEnum
from application.service.user.Model import UserModel
from application.util import TokenUtil


async def parse_token(authorization: str = Header(default="")) -> int:
    """
    解析Token拿到用户ID（不含验证）
    :param authorization: 从Header中获取authorization的值
    :return: 未知或无Token都为0
    """
    return await TokenUtil.get_user_id(token=authorization)


async def verify_token(request: Request, authorization: str = Header()) -> int:
    """
    验证Token
    :param request: 当前请求
    :param authorization: 从Header中获取authorization的值
    :return: 用户ID
    """
    # 权限中间件已验证过同一请求的 Token 和用户状态，无需重复访问 Redis/数据库。
    user_id = getattr(request.state, "auth_user_id", None)
    if user_id is None:
        user_id = await TokenUtil.get_user_id(token=authorization)
        user_exists = await UserModel.filter(id=user_id).exists() if user_id else False
    else:
        user_exists = request.state.auth_user_exists
    if not user_exists:
        raise BasicException(status_code=StatusCodeEnum.AUTHORITY_ERROR)
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
        raise BasicException(status_code=StatusCodeEnum.AUTHORITY_ERROR)
