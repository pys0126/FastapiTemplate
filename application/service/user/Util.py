from application.util.StringUtil import sha1_encode, md5_encode


def encode_password(password: str) -> str:
    """
    密码加密
    :param password: 密码
    :return: 加密后的密码
    """
    # sha1(md5)
    return sha1_encode(md5_encode(password))
