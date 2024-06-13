from application.config.DatabaseConfig import MysqlConfig

# 创建数据库配置
DATABASE_CONFIG: dict = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",  # MySQL or Mariadb
            "credentials": {
                "host": MysqlConfig.host,
                "port": MysqlConfig.port,
                "user": MysqlConfig.username,
                "password": MysqlConfig.password,
                "database": MysqlConfig.database_name,
                "echo": False
            }
        }
    },
    "apps": {
        "models": {
            "models": MysqlConfig.models,
            "default_connection": "default"
        }
    },
    "use_tz": False,  # 建议不要开启，不然存储日期时会有很多坑，时区转换在项目中手动处理更稳妥。
    "timezone": "Asia/Shanghai"
}
