"""
应用日志工具
"""

import os
from typing import Any

from loguru import logger

from application.config.ServerConfig import ServerConfig

# 每个进程独立注册文件输出，避免多worker同时轮转同一文件
_registered_sinks: dict[str, int] = {}


def _get_logger(log_type: str) -> Any:
    """
    获取绑定日志类型的logger，并按需注册文件输出
    :param log_type: 日志类型
    :return:
    """
    if log_type not in _registered_sinks:
        os.makedirs(ServerConfig.log_dir, exist_ok=True)
        process_id: int = os.getpid()
        log_file: str = os.path.join(
            ServerConfig.log_dir,
            f"{{time:YYYY-MM-DD}}.{process_id}.{log_type}.log",
        )
        sink_id: int = logger.add(
            log_file,
            rotation="10 MB",
            retention="7 days",
            encoding="utf-8",
            enqueue=True,
            backtrace=False,
            diagnose=False,
            filter=lambda record, current_type=log_type: (
                record["extra"].get("log_type") == current_type
            ),
        )
        _registered_sinks[log_type] = sink_id
    return logger.bind(log_type=log_type)


def write_error_log(log_message: str, traceback: str = "") -> None:
    """
    写入异常日志
    :param log_message: 日志信息
    :param traceback: 堆栈信息
    :return:
    """
    error_logger = _get_logger(log_type="error")
    error_logger.error(f"{log_message} - 异常堆栈信息 =>\n{traceback}")


def write_task_log(
    task_name: str, status: str, message: str = "", duration: float = 0.0
) -> None:
    """
    写入后台任务日志
    :param task_name: 任务名称
    :param status: 任务状态
    :param message: 日志信息
    :param duration: 任务执行耗时（毫秒）
    :return:
    """
    # 请求日志成功时不逐条写文件，但失败与超时必须保留
    if task_name == "write_request_log" and status not in {"failed", "timeout"}:
        return
    log_message: str = f"后台任务[{task_name}] 状态: {status}"
    if duration:
        log_message += f" 耗时: {duration:.2f}ms"
    if message:
        log_message += f" 信息 =>\n{message}"
    task_logger = _get_logger(log_type="background")
    if status in {"failed", "timeout"}:
        task_logger.error(log_message)
    elif status == "dropped":
        task_logger.warning(log_message)
    else:
        task_logger.info(log_message)
