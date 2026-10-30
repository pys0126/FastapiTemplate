"""普通 HTTP 请求的鉴权与日志开销测试。"""

import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from fastapi import Depends, FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.testclient import TestClient
from starlette.background import BackgroundTask

from application.dependency.AuthDependency import verify_token
from application.exception.BasicException import BasicException
from application.initial.BaseEnum import StatusCodeEnum
from application.middleware.PermissionMiddleware import PermissionMiddleware
from application.middleware.ProcessMiddleware import ProcessMiddleware
from application.service.user.Model import UserModel


class PermissionMiddlewareTest(unittest.TestCase):
    """无凭据时跳过鉴权 I/O，有凭据时复用请求内的结果。"""

    def setUp(self) -> None:
        app = FastAPI()
        app.add_middleware(PermissionMiddleware)
        app.add_exception_handler(BasicException, BasicException.exception_handler)

        @app.get("/public")
        async def public() -> dict[str, bool]:
            return {"ok": True}

        @app.get("/protected", dependencies=[Depends(verify_token)])
        async def protected() -> dict[str, bool]:
            return {"ok": True}

        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def test_anonymous_request_skips_redis_and_database(self) -> None:
        with (
            patch(
                "application.middleware.PermissionMiddleware.get_user_id",
                new_callable=AsyncMock,
            ) as get_user_id,
            patch.object(UserModel, "filter") as filter_user,
        ):
            response = self.client.get("/public")
        self.assertEqual(response.status_code, 200)
        get_user_id.assert_not_awaited()
        filter_user.assert_not_called()

    def test_protected_request_reuses_validation(self) -> None:
        with (
            patch(
                "application.middleware.PermissionMiddleware.get_user_id",
                new_callable=AsyncMock,
                return_value=7,
            ) as get_user_id,
            patch.object(UserModel, "filter") as filter_user,
            patch(
                "application.dependency.AuthDependency.TokenUtil.get_user_id",
                new_callable=AsyncMock,
            ) as redundant_check,
        ):
            filter_user.return_value.values_list.return_value.first = AsyncMock(
                return_value=False
            )
            response = self.client.get(
                "/protected", headers={"Authorization": "test-token"}
            )
        self.assertEqual(response.status_code, 200)
        get_user_id.assert_awaited_once_with(token="test-token")
        filter_user.assert_called_once_with(id=7)
        filter_user.return_value.values_list.assert_called_once_with(
            "is_disabled", flat=True
        )
        redundant_check.assert_not_awaited()

    def test_invalid_token_skips_database(self) -> None:
        with (
            patch(
                "application.middleware.PermissionMiddleware.get_user_id",
                new_callable=AsyncMock,
                return_value=0,
            ),
            patch.object(UserModel, "filter") as filter_user,
        ):
            response = self.client.get(
                "/protected", headers={"Authorization": "invalid"}
            )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], StatusCodeEnum.AUTHORITY_ERROR.code)
        filter_user.assert_not_called()

    def test_disabled_user_is_still_rejected(self) -> None:
        with (
            patch(
                "application.middleware.PermissionMiddleware.get_user_id",
                new_callable=AsyncMock,
                return_value=7,
            ),
            patch.object(UserModel, "filter") as filter_user,
        ):
            filter_user.return_value.values_list.return_value.first = AsyncMock(
                return_value=True
            )
            response = self.client.get(
                "/protected", headers={"Authorization": "test-token"}
            )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], StatusCodeEnum.USER_DISABLED.code)


class ProcessMiddlewareTest(unittest.IsolatedAsyncioTestCase):
    """日志入队在响应对象准备好后执行，不影响已有响应后台任务。"""

    async def test_enqueue_is_deferred_until_response_completion(self) -> None:
        app = FastAPI()
        app.state.task_pool = object()
        request = Request(
            {
                "type": "http",
                "method": "GET",
                "path": "/ping",
                "query_string": b"key=value",
                "headers": [],
                "client": ("127.0.0.1", 1234),
                "app": app,
            }
        )
        other_tasks: list[str] = []

        async def existing_task() -> None:
            other_tasks.append("existing")

        async def call_next(_request: Request) -> PlainTextResponse:
            return PlainTextResponse("ok", background=BackgroundTask(existing_task))

        with patch(
            "application.middleware.ProcessMiddleware.enqueue_task",
            new_callable=AsyncMock,
        ) as enqueue:
            response = await ProcessMiddleware(app).dispatch(request, call_next)
            enqueue.assert_not_awaited()
            self.assertIn("x-request-id", response.headers)
            await response.background()

        enqueue.assert_awaited_once()
        self.assertEqual(enqueue.await_args.args[1], "write_request_log")
        self.assertEqual(other_tasks, ["existing"])

    async def test_response_body_is_sent_before_slow_enqueue(self) -> None:
        app = FastAPI()
        app.state.task_pool = object()
        app.add_middleware(ProcessMiddleware)

        @app.get("/ping")
        async def ping() -> dict[str, bool]:
            return {"ok": True}

        sent_body = asyncio.Event()
        release_enqueue = asyncio.Event()
        first_receive = True

        async def receive() -> dict:
            nonlocal first_receive
            if first_receive:
                first_receive = False
                return {"type": "http.request", "body": b"", "more_body": False}
            await asyncio.Future()

        async def send(message: dict) -> None:
            if message["type"] == "http.response.body" and not message.get(
                "more_body", False
            ):
                sent_body.set()

        async def slow_enqueue(*_args: object, **_kwargs: object) -> None:
            await release_enqueue.wait()

        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "method": "GET",
            "scheme": "http",
            "path": "/ping",
            "raw_path": b"/ping",
            "query_string": b"",
            "headers": [],
            "client": ("127.0.0.1", 1234),
            "server": ("testserver", 80),
        }
        with patch(
            "application.middleware.ProcessMiddleware.enqueue_task",
            side_effect=slow_enqueue,
        ) as enqueue:
            task = asyncio.create_task(app(scope, receive, send))
            try:
                await asyncio.wait_for(sent_body.wait(), timeout=1)
                self.assertFalse(task.done())
                enqueue.assert_awaited_once()
            finally:
                release_enqueue.set()
                await asyncio.wait_for(task, timeout=1)


if __name__ == "__main__":
    unittest.main()
