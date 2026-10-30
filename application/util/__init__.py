from importlib import import_module
from pathlib import Path
from typing import Type
from fastapi import FastAPI
from application.config import PROJECT_ROOT

SERVICE_DIR: Path = PROJECT_ROOT / "application" / "service"
EXCEPTION_DIR: Path = PROJECT_ROOT / "application" / "exception"
MIDDLEWARE_DIR: Path = PROJECT_ROOT / "application" / "middleware"


def register_admin() -> None:
    """
    自动注册各后台管理
    :return:
    """
    for module in sorted(SERVICE_DIR.iterdir()):
        if module.is_dir() and (module / "Admin.py").is_file():
            import_module(name=f"application.service.{module.name}.Admin")


def register_routers(app: FastAPI) -> None:
    """
    自动注册各路由
    :param app: Fastapi对象
    :return:
    """
    for module in sorted(SERVICE_DIR.iterdir()):
        if module.is_dir() and (module / "Controller.py").is_file():
            controller: object = import_module(
                name=f"application.service.{module.name}.Controller"
            )
            if hasattr(controller, "router"):
                app.include_router(router=controller.router)


def register_exceptions(app: FastAPI) -> None:
    """
    自动注册各异常
    :param app: Fastapi对象
    :return:
    """
    for module in sorted(EXCEPTION_DIR.glob("*.py")):
        if module.name == "__init__.py":
            continue
        exception: object = import_module(name=f"application.exception.{module.stem}")
        exception_class: Type[Exception] = getattr(exception, module.stem)
        if hasattr(exception_class, "exception_handler"):
            app.add_exception_handler(exc_class_or_status_code=exception_class,
                                      handler=exception_class.exception_handler)


def register_middleware(app: FastAPI) -> None:
    """
    自动注册中间件
    :param app: Fastapi对象
    :return:
    """
    for module in sorted(MIDDLEWARE_DIR.glob("*.py")):
        if module.name == "__init__.py":
            continue
        middleware: object = import_module(name=f"application.middleware.{module.stem}")
        middleware_class: object = getattr(middleware, module.stem)
        app.add_middleware(middleware_class=middleware_class)


async def create_initial_user() -> None:
    """
    创建初始用户
    :return:
    """
    from application.service.user.Util import encode_password
    from application.service.user.Model import UserModel
    user_model: UserModel = UserModel(
        username="admin",
        password=encode_password("admin123"),
        nickname="初始超级用户",
        is_disabled=False,
        is_employee=True,
        is_superuser=True
    )
    if await UserModel.all().count() == 0:
        await user_model.save()
