"""ARQ worker配置。"""

from typing import Any, ClassVar

from tortoise import Tortoise

from application.config.WorkerConfig import WorkerConfig
from application.util.MysqlUtil import DATABASE_CONFIG
from application.util.RedisUtil import redis_util
from application.worker import REDIS_SETTINGS
from application.worker.Task import write_request_log


async def startup(_ctx: dict[str, Any]) -> None:
    """初始化任务使用的ORM连接。"""
    await Tortoise.init(config=DATABASE_CONFIG, _enable_global_fallback=True)


async def shutdown(_ctx: dict[str, Any]) -> None:
    """关闭任务使用的连接。"""
    try:
        await redis_util.clean()
    finally:
        await Tortoise.close_connections()


class WorkerSettings:
    """ARQ配置；新增任务时将任务函数加入functions。"""

    functions: ClassVar[list[Any]] = [write_request_log]
    redis_settings = REDIS_SETTINGS
    queue_name = WorkerConfig.queue_name
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = WorkerConfig.max_jobs
    job_timeout = WorkerConfig.job_timeout
    max_tries = WorkerConfig.max_tries
    keep_result = 0
    job_completion_wait = WorkerConfig.shutdown_timeout
