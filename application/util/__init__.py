import os
from typing import Type
from fastapi import FastAPI
from importlib import import_module

# 排除文件
exclude_file: list = ["__init__.py", "__pycache__"]


def register_admin() -> None:
    """
    自动注册各后台管理
    :return:
    """
    for module in os.listdir(path="application/service"):
        # 跳过排除文件
        if module in exclude_file:
            continue
        # 定义后台管理名称
        admin_name: str = "Admin"
        # 跳过非后台管理模块
        if not os.path.exists(f"application/service/{module}/{admin_name}.py"):
            continue
        # 导入后台管理
        import_module(name=f"application.service.{module}.{admin_name}")


def register_routers(app: FastAPI) -> None:
    """
    自动注册各路由
    :param app: Fastapi对象
    :return:
    """
    for module in os.listdir(path="application/service"):
        # 跳过排除文件
        if module in exclude_file:
            continue
        # 定义控制器名称
        controller_name: str = "Controller"
        # 跳过非控制器模块
        if not os.path.exists(f"application/service/{module}/{controller_name}.py"):
            continue
        # 导入控制器
        controller: object = import_module(name=f"application.service.{module}.{controller_name}")
        if hasattr(controller, "router"):
            app.include_router(router=controller.router)


def register_exceptions(app: FastAPI) -> None:
    """
    自动注册各异常
    :param app: Fastapi对象
    :return:
    """
    for module in os.listdir(path="application/exception"):
        # 跳过__init__.py文件
        if module in ["__init__.py", "__pycache__"]:
            continue
        exception: object = import_module(name=f"application.exception.{module[:-3]}")
        exception_class: Type[Exception] = getattr(exception, module[:-3])
        if hasattr(exception_class, "exception_handler"):
            app.add_exception_handler(exc_class_or_status_code=exception_class,
                                      handler=exception_class.exception_handler)


def register_middleware(app: FastAPI) -> None:
    """
    自动注册中间件
    :param app: Fastapi对象
    :return:
    """
    for module in os.listdir(path="application/middleware"):
        # 跳过__init__.py文件
        if module in ["__init__.py", "__pycache__"]:
            continue
        middleware: object = import_module(name=f"application.middleware.{module[:-3]}")
        middleware_class: object = getattr(middleware, module[:-3])
        app.add_middleware(middleware_class=middleware_class)


async def create_initial_user() -> None:
    """
    创建初始用户
    :return:
    """
    from application.service.user.Util import encode_password
    from application.service.user.Enum import UserSexEnum
    from application.service.user.Model import UserModel
    user_model: UserModel = UserModel(
        username="admin",
        password=encode_password("admin123"),
        nickname="初始超级用户",
        email="admin@admin.com",
        phone="12345678911",
        sex=UserSexEnum.MALE,
        is_disabled=False,
        is_employee=True,
        is_superuser=True,
        address="中国"
    )
    if await UserModel.all().count() == 0:
        await user_model.save()
