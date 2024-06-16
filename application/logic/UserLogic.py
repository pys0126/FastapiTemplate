import string
import random
from typing import Optional
from application.mapper.UserMapper import UserMapper
from application.enumeration.StatusCodeEnum import StatusCodeEnum
from application.exception.BasicException import BasicException
from application.util.StringUtil import md5_encode, sha1_encode
from application.entity.UserEntity import UserAdd, UserOut


def encode_password(password: str) -> str:
    """
    密码加密
    :param password: 密码
    :return: 加密后的密码
    """
    # sha1(md5)
    return sha1_encode(md5_encode(password))


async def generate_username(length: int = 10) -> str:
    """
    生成随机用户名
    :param length:
    :return:
    """
    prefix = "user_"
    characters = string.ascii_letters + string.digits
    random_part = "".join(random.choice(characters) for _ in range(length))
    username = prefix + random_part
    # 如果用户名已存在，则重新生成
    if await UserMapper.orm_model.exists(username=username):
        return await generate_username(length=length)
    return username


async def get_all_data(page: int, page_size: int) -> list[Optional[UserOut]]:
    """
    获取所有用户数据
    :return:
    """
    user_out_list: list = []
    for user_model in await UserMapper.get_data_list(page=page, page_size=page_size):
        user_out_list.append(UserOut(**user_model.to_dict()))
    return user_out_list


async def register(user_add: UserAdd) -> None:
    """
    注册用户
    :param user_add: 用户输入信息
    :return:
    """
    # 判断注册的邮箱、手机号是否已存在
    if user_add.email and await UserMapper.orm_model.exists(email=user_add.email):
        raise BasicException(status_code=StatusCodeEnum.ALREADY_EXIST_ERROR.value, message="邮箱已被注册！")
    if user_add.phone and await UserMapper.orm_model.exists(phone=user_add.phone):
        raise BasicException(status_code=StatusCodeEnum.ALREADY_EXIST_ERROR.value, message="手机号已被注册！")
    # 加密密码
    user_add.password = encode_password(password=user_add.password)
    # 转换为字典
    user_dict: dict = user_add.model_dump()
    # 生成用户名
    user_dict.update(username=await generate_username())
    # 存入数据
    if not await UserMapper.insert(data=user_dict):
        raise BasicException(status_code=StatusCodeEnum.BAD_REQUEST_ERROR.value, message="注册失败！")


async def login(user_add: UserAdd) -> None:
    """
    登录
    :param user_add: 用户输入信息
    :return:
    """

