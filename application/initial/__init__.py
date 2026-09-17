from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from application.util import create_initial_user
from application.util.RedisUtil import redis_util
from application.worker import close_task_pool, create_task_pool


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    主应用启动、关闭事件
    :param app: FastAPI应用
    :return:
    """
    # Web进程只负责向Redis提交任务，任务由独立ARQ worker消费
    task_pool = await create_task_pool()
    app.state.task_pool = task_pool
    try:
        # 创建初始用户（如果没有）
        await create_initial_user()
        yield
    finally:
        try:
            await close_task_pool(pool=task_pool)
        finally:
            await redis_util.clean()
