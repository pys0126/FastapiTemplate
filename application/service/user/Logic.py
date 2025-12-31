from typing import Optional
from application.service.user.Model import UserModel
from application.util.TokenUtil import generate_token
from application.initial.BaseEnum import StatusCodeEnum
from application.exception.BasicException import BasicException
from application.service.user.Entity import UserSearchOut, UserAdd, UserLogin, UserOut
from application.service.user.Util import verify_captcha, encode_password, generate_username
from application.util.StringUtil import is_valid_password, is_valid_phone_number, is_valid_email


async def get_all_data(page: int, page_size: int) -> list[Optional[UserSearchOut]]:
    """
    获取所有用户数据
    :return: 简易数据用户列表
    """
    user_out_list: list = []
    for user_model in await UserModel.get_data_list_by_fields(page=page, page_size=page_size):
        user_out: UserSearchOut = UserSearchOut(**user_model.to_dict())
        user_out.fans_num = len(user_model.fans_ids.split(",")) if user_model.fans_ids else 0  # 粉丝数
        user_out.follow_num = len(user_model.follow_ids.split(",")) if user_model.follow_ids else 0  # 关注数
        user_out_list.append(user_out)
    return user_out_list


async def register(user_add: UserAdd) -> None:
    """
    注册用户
    :param user_add: 用户输入信息
    :return:
    """
    # 验证手机号格式
    if user_add.phone:
        if not is_valid_phone_number(phone_number=str(user_add.phone)):
            raise BasicException(status_code=StatusCodeEnum.BAD_REQUEST_ERROR.value, message="手机号格式错误！")
        # 判断手机号是否已存在
        if await UserModel.exists(phone=user_add.phone):
            raise BasicException(status_code=StatusCodeEnum.ALREADY_EXIST_ERROR.value, message="手机号已被注册！")
    # 验证邮箱格式
    if user_add.email:
        if not is_valid_email(text=user_add.email):
            raise BasicException(status_code=StatusCodeEnum.BAD_REQUEST_ERROR.value, message="邮箱格式错误！")
        # 判断邮箱是否已存在
        if await UserModel.exists(email=user_add.email):
            raise BasicException(status_code=StatusCodeEnum.ALREADY_EXIST_ERROR.value, message="邮箱已被注册！")
        # 判断验证码是否正确
        if not verify_captcha(key=user_add.email, captcha=user_add.captcha):
            raise BasicException(status_code=StatusCodeEnum.AUTHORITY_ERROR.value, message="验证码错误！")
    # 验证密码格式
    if not is_valid_password(text=user_add.password):
        raise BasicException(status_code=StatusCodeEnum.BAD_REQUEST_ERROR.value,
                             message="密码最少6位，包含字母与数字，且不能包含特殊字符！")
    # 加密密码
    user_add.password = encode_password(password=user_add.password)
    # 转换为字典
    user_dict: dict = user_add.model_dump()
    # 生成用户名
    user_dict.update(username=await generate_username())
    # 存入数据
    if not await UserModel.create(**user_dict):
        raise BasicException(status_code=StatusCodeEnum.ERROR.value, message="服务器繁忙，请稍后重试！")


async def login(user_login: UserLogin) -> str:
    """
    登录
    :param user_login: 用户输入信息
    :return: Token
    """
    user_model: Optional[UserModel] = None
    if user_login.login_type == "username":
        # 验证密码格式
        if not is_valid_password(text=user_login.password):
            raise BasicException(status_code=StatusCodeEnum.BAD_REQUEST_ERROR.value,
                                 message="密码最少6位，包含字母与数字，且不能包含特殊字符！")
        user_model = await UserModel.filter(username=user_login.username).first()
    elif user_login.login_type == "email":
        # 验证邮箱格式
        if not is_valid_email(text=user_login.username):
            raise BasicException(status_code=StatusCodeEnum.BAD_REQUEST_ERROR.value, message="邮箱格式错误！")
        user_model = await UserModel.filter(email=user_login.username).first()
    elif user_login.login_type == "phone":
        # 验证手机号格式
        if not is_valid_phone_number(phone_number=user_login.username):
            raise BasicException(status_code=StatusCodeEnum.BAD_REQUEST_ERROR.value, message="手机号格式错误！")
        user_model = await UserModel.filter(phone=int(user_login.username)).first()
    # 验证用户是否存在
    if user_model is None:
        raise BasicException(status_code=StatusCodeEnum.NOT_FOUND_ERROR.value, message="该用户未注册！")
    # 如果是邮箱/手机号登录，判断验证码是否正确
    if user_login.login_type in ["email", "phone"]:
        # 判断验证码是否正确
        if not verify_captcha(key=user_login.username, captcha=user_login.captcha):
            raise BasicException(status_code=StatusCodeEnum.AUTHORITY_ERROR.value, message="验证码错误！")
    # 密码验证
    user_login.password = encode_password(password=user_login.password)
    if user_model.password != user_login.password:
        raise BasicException(status_code=StatusCodeEnum.AUTHORITY_ERROR.value, message="密码错误！")
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
        raise BasicException(status_code=StatusCodeEnum.NOT_FOUND_ERROR.value, message="该用户不存在！")
    return UserOut(**user_model.to_dict())
