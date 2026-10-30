"""通用模块验证码发送测试。"""

import asyncio
import threading
import unittest
from unittest.mock import AsyncMock, patch

from application.config import CAPTCHA_KEY
from application.config.ServerConfig import ServerConfig
from application.exception.BasicException import BasicException
from application.initial.BaseEnum import StatusCodeEnum
from application.service.common import Logic


class CaptchaEmailTest(unittest.IsolatedAsyncioTestCase):
    """同步 SMTP 不阻塞事件循环，发送成功后才保存验证码。"""

    async def test_email_send_runs_in_thread_and_saves_after_delivery(self) -> None:
        loop = asyncio.get_running_loop()
        main_thread_id = threading.get_ident()
        send_started = asyncio.Event()
        finish_send = threading.Event()
        send_thread_ids: list[int] = []

        def send_email(**_kwargs: str) -> bool:
            send_thread_ids.append(threading.get_ident())
            loop.call_soon_threadsafe(send_started.set)
            return finish_send.wait(timeout=2)

        with (
            patch.object(Logic.redis_util, "get_value", new_callable=AsyncMock, return_value=None),
            patch.object(Logic.redis_util, "set_value", new_callable=AsyncMock) as save,
            patch.object(Logic, "generate_verification_code", return_value="123456"),
            patch.object(Logic, "send_email", side_effect=send_email) as send,
        ):
            task = asyncio.create_task(
                Logic.send_captcha(target="test@example.com", send_type="email")
            )
            try:
                await asyncio.wait_for(send_started.wait(), timeout=1)
                self.assertEqual(len(send_thread_ids), 1)
                self.assertNotIn(main_thread_id, send_thread_ids)
                self.assertFalse(task.done())
                save.assert_not_awaited()
            finally:
                finish_send.set()
                await asyncio.wait_for(task, timeout=3)

        send.assert_called_once()
        save.assert_awaited_once_with(
            key=f"{CAPTCHA_KEY}test@example.com",
            value="123456",
            ex=ServerConfig.captcha_expire,
        )

    async def test_failed_email_does_not_save_captcha(self) -> None:
        with (
            patch.object(Logic.redis_util, "get_value", new_callable=AsyncMock, return_value=None),
            patch.object(Logic.redis_util, "set_value", new_callable=AsyncMock) as save,
            patch.object(Logic, "send_email", return_value=False),
        ):
            with self.assertRaises(BasicException) as error:
                await Logic.send_captcha(target="test@example.com", send_type="email")

        self.assertEqual(error.exception.status_code, StatusCodeEnum.CAPTCHA_SEND_ERROR)
        save.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
