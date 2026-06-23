from typing import Literal
from application.util.RedisUtil import redis_util
from application.util.EmailUtil import send_email
from application.initial.BaseEnum import StatusCodeEnum
from application.config import PROJECT_NAME, CAPTCHA_KEY
from application.config.ServerConfig import ServerConfig
from application.exception.BasicException import BasicException
from application.util.StringUtil import generate_verification_code, is_valid_email, is_valid_phone_number


async def send_captcha(target: str, send_type: Literal["email", "phone"]) -> None:
    """
    发送验证码
    :param target: 目标邮箱/手机号
    :param send_type: 发送类型（email/phone）
    :return:
    """
    # Redis的Key
    redis_key: str = CAPTCHA_KEY + target
    if send_type == "email":
        if await redis_util.get_value(key=redis_key) is not None:
            raise BasicException(status_code=StatusCodeEnum.EMAIL_CAPTCHA_ALREADY_SENT)
        # 检查邮箱格式
        if not is_valid_email(text=target):
            raise BasicException(status_code=StatusCodeEnum.EMAIL_FORMAT_ERROR)
        code: str = generate_verification_code()  # 生成验证码
        # 发送邮件
        result: bool = send_email(target_email=target, title=f"[{PROJECT_NAME}] 邮箱验证码",
                                  content=f"您的验证码是：{code}，"
                                          f"{int(ServerConfig.captcha_expire // 60)}分钟内有效")
    elif send_type == "phone":
        # TODO 模拟发送手机号验证码，实际按需求自定义对接云服务发送
        if await redis_util.get_value(key=redis_key) is not None:
            raise BasicException(status_code=StatusCodeEnum.PHONE_CAPTCHA_ALREADY_SENT)
        # 检查手机号格式
        if not is_valid_phone_number(phone_number=target):
            raise BasicException(status_code=StatusCodeEnum.PHONE_FORMAT_ERROR)
        code: str = generate_verification_code()  # 生成验证码
        # 发送手机号验证码
        result: bool = bool(code)
    else:
        raise BasicException(status_code=StatusCodeEnum.ILLEGALITY_ERROR)
    # 发送失败
    if not result:
        raise BasicException(status_code=StatusCodeEnum.CAPTCHA_SEND_ERROR)
    # 保存验证码到redis
    await redis_util.set_value(key=redis_key, value=code, ex=ServerConfig.captcha_expire)
