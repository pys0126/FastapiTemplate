from application.config.ServerConfig import ServerConfig
from loguru import logger
import os


# 指定日志文件
os.path.join(ServerConfig.log_dir, "{time}.logs.log")
log_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} - {message}"
logger.add(os.path.join(ServerConfig.log_dir, "{time}.logs.log"), rotation="10 MB", encoding="utf-8", retention="7 days")


def write_error_log(log_message: str, traceback: str = "") -> None:
    """
    写入异常日志
    :param log_message: 日志信息
    :param traceback: 堆栈信息
    :return:
    """
    log_message = f"{log_message} - 异常堆栈信息 =>\n{traceback}"
    logger.error(log_message)
