from fastapi import FastAPI
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from application.util.RedisUtil import redis_util


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    主应用启动、关闭事件
    :param app: FastAPI应用
    :return:
    """
    yield
    # 清理Redis资源
    await redis_util.clean()
