from application.config import PROJECT_NAME, CAPTCHA_KEY
from application.util.RedisUtil import redis_util
from application.util.EmailUtil import send_email
from application.config.EmailConfig import EmailConfig
from application.initial.BaseEnum import StatusCodeEnum
from application.exception.BasicException import BasicException
from application.util.StringUtil import generate_verification_code, is_valid_email


def email_captcha(email: str) -> None:
    """
    发送邮箱验证码
    :param email: 目标邮箱
    :return:
    """
    # Redis的Key
    redis_key: str = CAPTCHA_KEY + email
    if redis_util.get_value(key=redis_key) is not None:
        raise BasicException(status_code=StatusCodeEnum.ILLEGALITY_ERROR, message="已发送验证码，未找到请查看垃圾箱！")
    # 检查邮箱格式
    if not is_valid_email(text=email):
        raise BasicException(status_code=StatusCodeEnum.BAD_REQUEST_ERROR, message="请输入正确邮箱")
    code: str = generate_verification_code()  # 生成验证码
    # 发送邮件
    result: bool = send_email(target_email=email, title=f"[{PROJECT_NAME}] 邮箱验证码",
                              content=f"您的验证码是：{code}，"
                                      f"{int(EmailConfig.email_code_expire // 60)}分钟内有效")
    # 发送失败
    if not result:
        raise BasicException(status_code=StatusCodeEnum.ERROR, message="验证码发送失败，请稍后再试")
    # 保存验证码到redis
    redis_util.set_value(key=redis_key, value=code, ex=EmailConfig.email_code_expire)
