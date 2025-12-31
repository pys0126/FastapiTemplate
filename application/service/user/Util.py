import random
import string
from typing import Optional
from application.config import CAPTCHA_KEY
from application.service.user.Model import UserModel
from application.service.common.Logic import redis_client
from application.util.StringUtil import sha1_encode, md5_encode


async def verify_captcha(key: str, captcha: str) -> bool:
    """
    验证验证码
    :param key: 手机号/邮箱
    :param captcha: 验证码
    :return:
    """
    result: Optional[str] = await redis_client.get_value(key=CAPTCHA_KEY + key)
    if result is None or captcha != result:
        return False
    return True


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
    characters = string.ascii_letters + string.digits
    random_part = "".join(random.choice(characters) for _ in range(length))
    username = "user_" + random_part
    # 如果用户名已存在，则重新生成
    if await UserModel.exists(username=username):
        return await generate_username(length=length)
    return username