"""
数据库配置
"""
import os
from application.config import YAML_CONTENT


# 获取数据库配置
DATABASE_CONFIG: dict = YAML_CONTENT.get("DatabaseConfig")


def scan_models() -> list:
    """
    扫描ORM模型
    :return:
    """
    model_dir: str = os.path.join(os.getcwd(), "application", "model")
    result: list = []
    for file in os.listdir(model_dir):
        if file.endswith(".py") and file != "__init__.py":
            result.append(f"application.model.{file[:-3]}")
    return result


class MysqlConfig:
    """
    Mysql数据库配置
    """
    MYSQL_CONFIG: dict = DATABASE_CONFIG.get("MysqlConfig")  # 获取Mysql数据库配置项
    host: str = MYSQL_CONFIG.get("host", "127.0.0.1")  # 数据库主机名
    port: int = int(MYSQL_CONFIG.get("port", 3306))  # 数据库端口
    username: str = MYSQL_CONFIG.get("username", "root")  # 数据库用户名
    password: str = MYSQL_CONFIG.get("password", "root")  # 数据库密码
    database_name: str = MYSQL_CONFIG.get("database_name", "task_system")  # 数据库名称
    auto_create_table: bool = MYSQL_CONFIG.get("auto_create_table", False)  # 是否自动创建表
    models: list = scan_models()  # 扫描模型


class RedisConfig:
    """
    Redis配置
    """
    REDIS_CONFIG: dict = DATABASE_CONFIG.get("RedisConfig")  # 获取Redis配置项
    host: str = REDIS_CONFIG.get("host", "127.0.0.1")  # Redis主机名
    port: int = int(REDIS_CONFIG.get("port", 6379))  # Redis端口
    password: str = REDIS_CONFIG.get("password", "")  # Redis密码
    db: int = REDIS_CONFIG.get("db", 0)  # Redis数据库


