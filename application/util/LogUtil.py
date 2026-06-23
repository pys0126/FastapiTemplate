from application.config.ServerConfig import ServerConfig
from loguru import logger
import os


# 已注册的日志文件集合，避免重复添加 sink 导致日志重复输出
_registered_log_files: set = set()


def write_error_log(log_message: str, traceback: str = "") -> None:
    """
    写入异常日志
    :param log_message: 日志信息
    :param traceback: 堆栈信息
    :return:
    """
    # 指定日志文件
    log_file: str = os.path.join(ServerConfig.log_dir, "{time:YYYY-MM-DD}.error.log")
    # 仅在首次使用时注册 sink，避免重复添加导致日志重复输出
    if log_file not in _registered_log_files:
        logger.add(log_file, rotation="10 MB", encoding="utf-8", retention="7 days")
        _registered_log_files.add(log_file)
    log_message = f"{log_message} - 异常堆栈信息 =>\n{traceback}"
    logger.error(log_message)


def write_task_log(task_name: str, status: str, message: str = "", duration: float = 0.0) -> None:
    """
    写入后台任务日志
    :param task_name: 任务名称
    :param status: 任务状态（started/completed/failed）
    :param message: 日志信息
    :param duration: 任务执行耗时（毫秒）
    :return:
    """
    # 忽略请求日志
    if task_name == "write_request_log":
        return
    # 指定日志文件
    log_file: str = os.path.join(ServerConfig.log_dir, "{time:YYYY-MM-DD}.background.log")
    # 仅在首次使用时注册 sink，避免重复添加导致日志重复输出
    if log_file not in _registered_log_files:
        logger.add(log_file, rotation="10 MB", encoding="utf-8", retention="7 days")
        _registered_log_files.add(log_file)
    # 拼接日志信息
    log_message = f"后台任务[{task_name}] 状态: {status}"
    if duration:
        log_message += f" 耗时: {duration:.2f}ms"
    if message:
        log_message += f" 信息 =>\n{message}"
    logger.info(log_message)
