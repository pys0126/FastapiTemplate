"""用户接口测试：只挂载目标路由，避免依赖生产中间件和外部服务。"""

import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from application.service.user.Controller import router
from application.service.user import Logic
from application.service.user.Entity import UserAdd, UserLogin
from application.service.user.Model import UserModel
from application.initial.BaseEntity import PagingEntity
from application.initial.BaseEnum import StatusCodeEnum
from application.exception.BasicException import BasicException


class UserControllerTest(unittest.TestCase):
    """验证用户接口的参数和统一响应。"""

    def setUp(self) -> None:
        test_app = FastAPI()
        test_app.include_router(router)
        self.client = TestClient(test_app)
        self.addCleanup(self.client.close)

    def test_get_all_data(self) -> None:
        """列表接口返回分页数据的统一响应。"""
        paging = {"page": 1, "page_size": 10, "total": 0, "items": []}
        with patch(
            "application.service.user.Logic.get_all_data",
            new_callable=AsyncMock,
            return_value=paging,
        ) as get_all_data:
            response = self.client.get("/user/all", params={"page": 1, "page_size": 10})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"code": 2000, "data": paging, "message": "ok"})
        get_all_data.assert_awaited_once_with(page=1, page_size=10)

    def test_register(self) -> None:
        """注册接口调用业务逻辑并返回成功响应。"""
        with patch(
            "application.service.user.Logic.register", new_callable=AsyncMock
        ) as register:
            response = self.client.post(
                "/user/register",
                json={"username": "tester", "nickname": "测试用户", "password": "abc123"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"code": 2000, "data": None, "message": "ok"})
        register.assert_awaited_once()
        self.assertEqual(register.await_args.kwargs["user_add"].username, "tester")
        self.assertEqual(register.await_args.kwargs["user_add"].nickname, "测试用户")

    def test_register_rejects_invalid_nickname(self) -> None:
        """无效入参在进入业务逻辑前被拒绝。"""
        with patch(
            "application.service.user.Logic.register", new_callable=AsyncMock
        ) as register:
            response = self.client.post(
                "/user/register",
                json={"username": "tester", "nickname": "x", "password": "abc123"},
            )

        self.assertEqual(response.status_code, 422)
        register.assert_not_awaited()

    def test_register_requires_username(self) -> None:
        """注册必须提供用户名。"""
        with patch(
            "application.service.user.Logic.register", new_callable=AsyncMock
        ) as register:
            response = self.client.post(
                "/user/register", json={"nickname": "测试用户", "password": "abc123"}
            )

        self.assertEqual(response.status_code, 422)
        register.assert_not_awaited()

    def test_login_with_username_and_password(self) -> None:
        """登录仅使用用户名和密码。"""
        with patch(
            "application.service.user.Logic.login",
            new_callable=AsyncMock,
            return_value="test-token",
        ) as login:
            response = self.client.post(
                "/user/login", json={"username": "tester", "password": "abc123"}
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"], "test-token")
        login.assert_awaited_once()
        self.assertEqual(login.await_args.kwargs["user_login"].username, "tester")

    def test_register_rejects_removed_fields(self) -> None:
        """旧的邮箱、手机号和验证码不再是注册入参。"""
        with patch(
            "application.service.user.Logic.register", new_callable=AsyncMock
        ) as register:
            response = self.client.post(
                "/user/register",
                json={
                    "username": "tester",
                    "nickname": "测试用户",
                    "password": "abc123",
                    "email": "test@example.com",
                },
            )

        self.assertEqual(response.status_code, 422)
        register.assert_not_awaited()

    def test_login_rejects_removed_login_type(self) -> None:
        """登录不再接受邮箱或手机登录方式。"""
        with patch(
            "application.service.user.Logic.login", new_callable=AsyncMock
        ) as login:
            response = self.client.post(
                "/user/login",
                json={"username": "tester", "password": "abc123", "login_type": "email"},
            )

        self.assertEqual(response.status_code, 422)
        login.assert_not_awaited()


class UserLogicTest(unittest.IsolatedAsyncioTestCase):
    """验证精简后的用户资料在业务层的读写行为。"""

    def test_model_retains_permission_fields(self) -> None:
        """模型只保留基本资料、权限标记和通用字段。"""
        self.assertEqual(set(UserModel._meta.fields_map), {
            "id", "create_datetime", "update_datetime", "username", "avatar",
            "nickname", "password", "intro", "is_disabled", "is_employee", "is_superuser",
        })

    async def test_register_saves_only_current_fields(self) -> None:
        """注册保存用户名、昵称、密码以及提交的可选资料。"""
        user_add = UserAdd(
            username="tester",
            nickname="测试用户",
            password="abc123",
            avatar="https://example.com/avatar.png",
            intro="个人简介",
        )
        with (
            patch("application.service.user.Logic.UserModel.exists", new_callable=AsyncMock, return_value=False) as exists,
            patch("application.service.user.Logic.UserModel.create", new_callable=AsyncMock, return_value=object()) as create,
        ):
            await Logic.register(user_add)

        exists.assert_awaited_once_with(username="tester")
        create.assert_awaited_once_with(
            username="tester",
            nickname="测试用户",
            password=Logic.encode_password("abc123"),
            avatar="https://example.com/avatar.png",
            intro="个人简介",
        )
        self.assertEqual(user_add.password, "abc123")

    async def test_register_rejects_duplicate_username(self) -> None:
        """用户名重复时不创建用户。"""
        user_add = UserAdd(username="tester", nickname="测试用户", password="abc123")
        with (
            patch("application.service.user.Logic.UserModel.exists", new_callable=AsyncMock, return_value=True),
            patch("application.service.user.Logic.UserModel.create", new_callable=AsyncMock) as create,
        ):
            with self.assertRaises(BasicException) as error:
                await Logic.register(user_add)

        self.assertEqual(error.exception.status_code, StatusCodeEnum.ALREADY_EXIST_ERROR)
        create.assert_not_awaited()

    async def test_login_queries_username_only(self) -> None:
        """使用用户名检索并核对密码后生成 Token。"""
        user_login = UserLogin(username="tester", password="abc123")
        user_model = SimpleNamespace(id=42, password=Logic.encode_password("abc123"))
        with (
            patch("application.service.user.Logic.UserModel.filter") as filter_user,
            patch("application.service.user.Logic.generate_token", new_callable=AsyncMock, return_value="test-token") as token,
        ):
            filter_user.return_value.first = AsyncMock(return_value=user_model)
            result = await Logic.login(user_login)

        self.assertEqual(result, "test-token")
        filter_user.assert_called_once_with(username="tester")
        token.assert_awaited_once_with(user_id=42)
        self.assertEqual(user_login.password, "abc123")

    async def test_list_excludes_password_and_removed_fields(self) -> None:
        """列表仅返回公开资料及原有禁用标记。"""
        now = datetime(2026, 1, 1)
        user_data = {
            "id": 42,
            "username": "tester",
            "nickname": "测试用户",
            "password": "hashed-password",
            "avatar": "https://example.com/avatar.png",
            "intro": "个人简介",
            "is_disabled": False,
            "create_datetime": now,
            "update_datetime": now,
            "email": "legacy@example.com",
        }
        paging = PagingEntity(page=1, page_size=10, total=1, items=[SimpleNamespace(to_dict=lambda: user_data)])
        with patch(
            "application.service.user.Logic.UserModel.get_data_list_by_fields",
            new_callable=AsyncMock,
            return_value=paging,
        ):
            result = await Logic.get_all_data(page=1, page_size=10)

        self.assertEqual(set(result.items[0].model_dump()), {
            "id", "username", "nickname", "avatar", "intro", "is_disabled",
            "create_datetime", "update_datetime",
        })


if __name__ == "__main__":
    unittest.main()
