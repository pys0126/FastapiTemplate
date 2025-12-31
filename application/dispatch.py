"""
定时任务包
"""
from application.service.common.Model import SystemRequestLogModel
from application.util.TokenUtil import get_user_id
from starlette.datastructures import QueryParams
from typing import Optional
from asyncio import Task
import asyncio
import orjson


# 存储后台任务集合
background_tasks: set = set()


def add_task(func: callable, *args, **kwargs) -> None:
    """
    添加任务
    :param func: 执行的函数
    :param args: 参数列表
    :param kwargs: 参数字典
    :return:
    """
    # 添加后台定时任务
    task: Task = asyncio.create_task(func(*args, **kwargs))
    # 将任务加入集合。 这将创建一个强引用。
    background_tasks.add(task)
    # 为避免永远保留对已结束任务的引用，
    # 让每个任务在完成后将对自己的引用
    # 移出集合：
    task.add_done_callback(background_tasks.discard)


async def write_request_log(token: str, request_body: str, request_ip: str, method: str, url_path: str,
                            query_params: QueryParams, request_id: str) -> None:
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
        request_query=orjson.dumps(dict(query_params)).decode("utf-8"),
        request_id=request_id
    )
