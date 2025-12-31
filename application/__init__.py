import os
import logging
import platform
from fastapi import FastAPI
from application.initial import lifespan
from application.config import PROJECT_NAME
from fastapi.middleware.cors import CORSMiddleware
from application.util.TimeUtil import now_format_date
from application.initial.BaseController import router
from application.util.MysqlUtil import DATABASE_CONFIG
from tortoise.contrib.fastapi import register_tortoise
from application.exception import low_exception_handler
from application.config.DatabaseConfig import MysqlConfig
from application.config.ServerConfig import ServerConfig, CORSConfig
from application.middleware.ProcessMiddleware import ProcessMiddleware
from application.util import register_routers, register_exceptions, register_middleware

# 加速事件循环
if platform.system() == "Linux":
    import uvloop
    uvloop.install()

# 创建日志目录（如果不存在）
os.makedirs(name=ServerConfig.log_dir, exist_ok=True)

# 配置Tortoise ORM日志等级
logger: logging.Logger = logging.getLogger("tortoise")
logger.setLevel(logging.INFO)

# 创建FastAPI实例，关闭接口文档；注册应用开始、结束事件
app: FastAPI = FastAPI(title=PROJECT_NAME, description=PROJECT_NAME, docs_url=None, redoc_url=None, lifespan=lifespan)
# 注册Tortoise ORM
register_tortoise(app=app, config=DATABASE_CONFIG, generate_schemas=MysqlConfig.auto_create_table)

# 自动配置自定义中间件
register_middleware(app=app)
# 配置CORS跨域中间件
app.add_middleware(middleware_class=CORSMiddleware, allow_origins=CORSConfig.allow_origins,
                   allow_methods=CORSConfig.allow_methods, allow_headers=CORSConfig.allow_headers)

# 自动配置自定义路由
register_routers(app=app)
app.include_router(router=router)  # 根路由

# 自动配置自定义异常
register_exceptions(app=app)
# 配置低级异常
app.add_exception_handler(exc_class_or_status_code=Exception, handler=low_exception_handler)
