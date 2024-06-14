import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from application.util.MysqlUtil import DATABASE_CONFIG
from tortoise.contrib.fastapi import register_tortoise
from application.exception import low_exception_handler
from application.depend.TokenDepend import verify_token
from application.exception.BasicException import BasicException
from application.config.ServerConfig import ServerConfig, CORSConfig
from application.controller import IndexController, UserController

# 创建日志目录（如果不存在）
os.makedirs(name=ServerConfig.log_dir, exist_ok=True)

# 创建FastAPI实例
app: FastAPI = FastAPI(title="Test", description="Test System")
# 注册Tortoise ORM
register_tortoise(app=app, config=DATABASE_CONFIG, generate_schemas=True)  # 生产环境generate_schemas设置为False

# 配置CORS跨域中间件
app.add_middleware(middleware_class=CORSMiddleware, allow_origins=CORSConfig.allow_origins, 
                   allow_methods=CORSConfig.allow_methods, allow_headers=CORSConfig.allow_headers)

# 配置路由、添加依赖
app.include_router(router=IndexController.router)
app.include_router(router=UserController.router)

# 配置异常
app.add_exception_handler(exc_class_or_status_code=BasicException, handler=BasicException.exception_handler)
app.add_exception_handler(exc_class_or_status_code=Exception, handler=low_exception_handler)
