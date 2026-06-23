"""
后台任务模块
"""
from application.service.common.Model import SystemRequestLogModel
from application.util.TokenUtil import get_user_id
from application.util.LogUtil import write_task_log
from typing import Optional, Callable
from asyncio import Task
import asyncio
import time
import traceback


# 存储后台任务集合
background_tasks: set = set()


def add_task(func: Callable, *args, **kwargs) -> None:
    """
    添加后台任务
    :param func: 执行的函数
    :param args: 参数列表
    :param kwargs: 参数字典
    :return:
    """
    async def _execute_task(_func: Callable, *_args, **_kwargs) -> None:
        """
        执行后台任务（带日志记录与异常捕获）
        :param _func: 执行的函数
        :param _args: 参数列表
        :param _kwargs: 参数字典
        :return:
        """
        # 获取任务名称
        task_name: str = getattr(_func, "__name__", str(_func))
        # 记录任务开始日志
        write_task_log(task_name=task_name, status="started")
        # 记录开始时间
        start_time: float = time.perf_counter()
        try:
            # 执行任务
            await _func(*_args, **_kwargs)
            # 计算耗时（毫秒）
            duration: float = (time.perf_counter() - start_time) * 1000
            # 记录任务完成日志
            write_task_log(task_name=task_name, status="completed", duration=duration)
        except Exception as exception:
            # 计算耗时（毫秒）
            duration: float = (time.perf_counter() - start_time) * 1000
            # 记录任务失败日志
            write_task_log(
                task_name=task_name,
                status="failed",
                message=f"{exception}\n{traceback.format_exc()}",
                duration=duration
            )
    # 添加后台定时任务，通过 _execute_task 包装以记录日志与捕获异常
    task: Task = asyncio.create_task(_execute_task(func, *args, **kwargs))
    # 将任务加入集合，这将创建一个强引用。
    background_tasks.add(task)
    # 为避免永远保留对已结束任务的引用，
    # 让每个任务在完成后将对自己的引用
    # 移出集合：
    task.add_done_callback(background_tasks.discard)


async def write_request_log(token: str, request_body: Optional[str], request_ip: str, method: str, url_path: str,
                            query_params: Optional[str], request_id: str) -> None:
    """
    写入请求日志到数据库
    :param token: 用户Token
    :param request_body: 请求体
    :param request_ip: 请求IP
    :param method: 请求方法
    :param url_path: URL路径
    :param query_params: GET参数
    :param request_id: 请求ID
    :return:
    """
    # 获取用户ID
    user_id: Optional[int] = await get_user_id(token=token) or None
    # 写入请求日志表
    await SystemRequestLogModel.create(
        user_id=user_id,
        request_body=request_body,
        request_ip=request_ip,
        request_method=method,
        request_path=url_path,
        request_query=query_params,
        request_id=request_id
    )
