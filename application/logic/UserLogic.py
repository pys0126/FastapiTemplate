from typing import Optional
from application.model.UserModel import UserModel
from application.mapper.UserMapper import UserMapper
from application.enumeration.StatusCodeEnum import StatusCodeEnum
from application.exception.BasicException import BasicException
from application.util.StringUtil import md5_encode, sha1_encode
from application.entity.UserEntity import UserIn, UserOut


def encode_password(password: str) -> str:
    """
    密码加密
    :param password: 密码
    :return: 加密后的密码
    """
    # sha1(md5)
    return sha1_encode(md5_encode(password))

async def get_all_data(page: int, page_size: int) -> list[Optional[UserOut]]:
    """
    获取所有用户数据
    :return:
    """
    user_out_list: list = []
    for user_model in await UserMapper.get_data_list(page=page, page_size=page_size):
        print(user_model.to_dict())
        user_out_list.append(UserOut(**user_model.to_dict()))
    return user_out_list

async def register(user_in: UserIn) -> None:
    """
    注册用户
    :param user_in: 用户输入信息
    :return:
    """
    user_in.password = encode_password(password=user_in.password)
    if not await UserMapper.insert(data=user_in.model_dump()):
        raise BasicException(status_code=StatusCodeEnum.BAD_REQUEST_ERROR.value, message="注册失败！")