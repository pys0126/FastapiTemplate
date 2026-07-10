from fastapi.testclient import TestClient
from functools import wraps
from application import app
from httpx2 import Response
from loguru import logger
import json


def with_test(username: str = "admin", password: str = "admin123"):
    """
    测试装饰器，自动登录
    :param username: 登录用户名
    :param password: 登录密码
    :return:
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 自动登录
            with TestClient(app) as test_client:
                response: Response = test_client.post("/user/login", json={
                    "username": username,
                    "password": password,
                    "login_type": "username"
                })
            # 自动登录成功，设置测试客户端
            with TestClient(app, headers={"Authorization": response.json().get("data")}) as test_client:
                logger.info(json.dumps(func(*args, test_client=test_client, **kwargs), ensure_ascii=False, indent=4))
        return wrapper
    return decorator
