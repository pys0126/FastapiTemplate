import os
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from application.controller import IndexController
from application.exception import low_exception_handler
from application.util.MysqlUtil import DATABASE_CONFIG
from application.config.ServerConfig import ServerConfig
from application.config.DatabaseConfig import RedisConfig
from application.enumeration.StatusCodeEnum import StatusCodeEnum
from application.exception.BasicException import BasicException
from fastapi.middleware.cors import CORSMiddleware

# 创建日志目录（如果不存在）
os.makedirs(name=ServerConfig.log_dir, exist_ok=True)

# 创建FastAPI实例
app: FastAPI = FastAPI(title="Test", description="Test System")
# 注册Tortoise ORM
register_tortoise(app=app, config=DATABASE_CONFIG, generate_schemas=True)

# 配置跨域中间件，所有域都可以访问
app.add_middleware(middleware_class=CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
# 配置路由
app.include_router(router=IndexController.router)
# 配置异常
app.add_exception_handler(exc_class_or_status_code=BasicException, handler=BasicException.exception_handler)
app.add_exception_handler(exc_class_or_status_code=Exception, handler=low_exception_handler)
