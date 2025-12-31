from application.config.DatabaseConfig import MysqlConfig
from dbutils.pooled_db import PooledDB
from pymysql.cursors import DictCursor
from pymysql import Connection
import pymysql

# 创建tortoise数据库配置
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


class MysqlUtil:
    """
    Mysql数据库工具类，独立于FastAPI应用
    """

    def __init__(self, host: str = MysqlConfig.host, port: int = MysqlConfig.port,
                 username: str = MysqlConfig.username, password: str = MysqlConfig.password,
                 database_name: str = MysqlConfig.database_name) -> None:
        # 创建数据库连接池
        self.pool: PooledDB = PooledDB(creator=pymysql, blocking=True, host=host, port=port,
                                       user=username, passwd=password, db=database_name, charset="utf8mb4")

    def get_connection(self) -> tuple[Connection, DictCursor]:
        """
        获取连接和游标
        :return: （连接对象，游标对象）
        """
        connection: Connection = self.pool.connection()
        cursor: DictCursor = connection.cursor(cursor=DictCursor)
        return connection, cursor

    def fetch_one(self, sql: str, params: list = None) -> dict:
        """
        执行SQL语句，获取一条结果
        :param sql: SQL语句
        :param params: 需要传入的参数
        :return:
        """
        connection, cursor = self.get_connection()
        cursor.execute(query=sql, args=params)
        result: dict = cursor.fetchone()
        MysqlUtil.close_connection(connection=connection, cursor=cursor)
        return result

    def fetch_all(self, sql: str, params: list = None) -> tuple:
        """
        执行SQL语句，获取所有结果
        :param sql: SQL语句
        :param params: 需要传入的参数
        :return:
        """
        connection, cursor = self.get_connection()
        cursor.execute(query=sql, args=params)
        result: tuple = cursor.fetchall()
        MysqlUtil.close_connection(connection=connection, cursor=cursor)
        return result

    def commit_sql(self, sql: str, params: list = None) -> int:
        """
        执行SQL操作数据
        :param sql: SQL语句
        :param params: 需要传入的参数
        :return: 受影响条数
        """
        connection, cursor = self.get_connection()
        row_count: int = cursor.execute(query=sql, args=params)
        connection.commit()
        MysqlUtil.close_connection(connection=connection, cursor=cursor)
        return row_count

    @staticmethod
    def close_connection(connection: Connection, cursor: DictCursor) -> None:
        """
        关闭连接和游标
        :param connection: 连接对象
        :param cursor: 游标对象
        :return:
        """
        cursor.close()
        connection.close()
