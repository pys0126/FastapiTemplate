from typing import Optional
from application.service.user.Model import UserModel
from application.util.TokenUtil import generate_token
from application.initial.BaseEntity import PagingEntity
from application.initial.BaseEnum import StatusCodeEnum
from application.exception.BasicException import BasicException
from application.service.user.Entity import UserAdd, UserLogin, UserOut
from application.service.user.Util import encode_password
from application.util.StringUtil import is_valid_password


async def get_all_data(page: int, page_size: int) -> PagingEntity:
    """
    获取所有用户数据
    :return: 用户资料分页列表
    """
    paging_entity: PagingEntity = await UserModel.get_data_list_by_fields(page=page, page_size=page_size,
                                                                          return_model=True)
    paging_entity.items = [UserOut(**user_model.to_dict()) for user_model in paging_entity.items]
    return paging_entity


async def register(user_add: UserAdd) -> None:
    """
    注册用户
    :param user_add: 用户输入信息
    :return:
    """
    # 判断用户名是否已存在
    if await UserModel.exists(username=user_add.username):
        raise BasicException(status_code=StatusCodeEnum.ALREADY_EXIST_ERROR)
    # 验证密码格式
    if not is_valid_password(text=user_add.password):
        raise BasicException(status_code=StatusCodeEnum.PASSWORD_FORMAT_ERROR)
    # 只保存用户资料和加密后的密码，未提交的可选资料使用模型默认值
    user_dict: dict = user_add.model_dump(mode="json", exclude_none=True)
    user_dict["password"] = encode_password(password=user_add.password)
    # 存入数据
    if not await UserModel.create(**user_dict):
        raise BasicException(status_code=StatusCodeEnum.SERVER_BUSY)


async def login(user_login: UserLogin) -> str:
    """
    登录
    :param user_login: 用户输入信息
    :return: Token
    """
    # 验证密码格式
    if not is_valid_password(text=user_login.password):
        raise BasicException(status_code=StatusCodeEnum.PASSWORD_FORMAT_ERROR)
    user_model: Optional[UserModel] = await UserModel.filter(username=user_login.username).first()
    # 验证用户是否存在
    if user_model is None:
        raise BasicException(status_code=StatusCodeEnum.USER_NOT_REGISTERED)
    # 密码验证
    if user_model.password != encode_password(password=user_login.password):
        raise BasicException(status_code=StatusCodeEnum.PASSWORD_ERROR)
    # 生成Token
    return await generate_token(user_id=user_model.id)


async def get_user_by_id(user_id: int) -> UserOut:
    """
    根据ID获取用户信息
    :param user_id: 用户ID
    :return: 用户详细信息
    """
    user_model: Optional[UserModel] = await UserModel.filter(id=user_id).first()
    if not user_model:
        raise BasicException(status_code=StatusCodeEnum.USER_NOT_FOUND)
    return UserOut(**user_model.to_dict())
