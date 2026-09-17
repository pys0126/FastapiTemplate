"""ARQ任务生产端。"""

import asyncio
from typing import Any

from arq.connections import ArqRedis, RedisSettings, create_pool
from arq.jobs import Job

from application.config.DatabaseConfig import RedisConfig
from application.config.WorkerConfig import WorkerConfig
from application.util.LogUtil import write_task_log

REDIS_SETTINGS = RedisSettings(
    host=RedisConfig.host,
    port=RedisConfig.port,
    database=RedisConfig.db,
    password=RedisConfig.password or None,
)


async def create_task_pool() -> ArqRedis:
    """创建Web进程使用的ARQ连接池。"""
    return await create_pool(
        REDIS_SETTINGS,
        default_queue_name=WorkerConfig.queue_name,
    )


async def close_task_pool(pool: ArqRedis) -> None:
    """关闭ARQ连接池。"""
    await pool.aclose()


async def enqueue_task(
    pool: ArqRedis | None,
    function: str,
    *args: Any,
    **kwargs: Any,
) -> Job | None:
    """提交ARQ任务；队列异常不影响当前业务请求。"""
    if pool is None:
        return None
    try:
        async with asyncio.timeout(WorkerConfig.enqueue_timeout):
            return await pool.enqueue_job(function, *args, **kwargs)
    except Exception as exception:
        write_task_log(
            task_name=function,
            status="failed",
            message=f"enqueue failed: {type(exception).__name__}: {exception}",
        )
        return None
