"""
邮箱配置
"""
from application.config import YAML_CONTENT


class EmailConfig:
    EMAIL_CONFIG: dict = YAML_CONTENT.get("EmailConfig")
    email_from: str = EMAIL_CONFIG.get("email_from", "")  # 发件人邮箱
    email_password: str = EMAIL_CONFIG.get("email_password", "")  # 发件人邮箱密码/授权码
