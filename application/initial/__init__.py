from fastapi import FastAPI
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from application.util import create_initial_user
from application.util.RedisUtil import redis_util


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    主应用启动、关闭事件
    :param app: FastAPI应用
    :return:
    """
    # 创建初始用户（如果没有）
    await create_initial_user()
    yield
    # 清理Redis资源
    await redis_util.clean()
