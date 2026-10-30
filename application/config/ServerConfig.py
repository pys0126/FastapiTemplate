"""
服务器配置
"""
import os
from datetime import timedelta
from pathlib import Path
from application.config import PROJECT_ROOT, YAML_CONTENT


class ServerConfig:
    SERVER_CONFIG: dict = YAML_CONTENT.get("ServerConfig") or {}  # 获取服务器配置
    # 服务器配置项
    host: str = SERVER_CONFIG.get("host", "0.0.0.0")  # 服务访问地址
    port: int = int(SERVER_CONFIG.get("port", 6868))  # 服务访问端口
    workers: int = int(SERVER_CONFIG.get("workers", 1))  # 服务的进程数

    # 其他配置项
    # 相对路径固定以项目目录为基准，避免从其他目录启动时写到意外位置。
    log_dir: str = str(
        (PROJECT_ROOT / Path(SERVER_CONFIG.get("log_dir", "logs"))).resolve()
    )
    # Token过期时间，默认7天
    token_expire: int = int(SERVER_CONFIG.get("token_expire", int(timedelta(days=7).total_seconds())))
    secret_key: str = os.environ.get(
        "APP_SECRET_KEY", SERVER_CONFIG.get("secret_key", "")
    )  # Token加密密钥，所有进程必须一致
    if not isinstance(secret_key, str) or not secret_key.strip():
        raise ValueError("请配置 ServerConfig.secret_key 或 APP_SECRET_KEY，所有进程需使用相同密钥")
    # 验证码过期时间（秒），默认5分钟
    captcha_expire: int = int(SERVER_CONFIG.get("captcha_expire", 300))

    file_max_size: int = int(SERVER_CONFIG.get("file_max_size", 1024 * 1024 * 3))  # 文件最大上传大小（字节），默认3M

    # 默认超级管理员
    super_admin_username: str = SERVER_CONFIG.get("super_admin_username", "admin")  # 用户名
    super_admin_password: str = SERVER_CONFIG.get("super_admin_password", "admin")  # 密码


class CORSConfig:
    CORS_CONFIG: dict = ServerConfig.SERVER_CONFIG.get("CORSConfig") or {}
    allow_origins: list = CORS_CONFIG.get("allow_origins", ["*"])
    allow_methods: list = CORS_CONFIG.get("allow_methods", ["*"])
    allow_headers: list = CORS_CONFIG.get("allow_headers", ["*"])
