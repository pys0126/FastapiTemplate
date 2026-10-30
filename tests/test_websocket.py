"""WebSocket 通知等待与发送测试，不依赖真实 Redis。"""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import orjson

from application.config import WEBSOCKET_KEY
from application.initial.BaseController import websocket_endpoint
from application.initial.BaseEnum import WebsocketNoticeTypeEnum
from application.util.RedisUtil import redis_util
from application.util.WebSocketUtil import WebSocketUtil


class FakeWebSocket:
    """只模拟通知发送和客户端断开事件。"""

    def __init__(self) -> None:
        self.disconnected = asyncio.Event()
        self.sent = asyncio.Event()
        self.messages: list[dict] = []

    async def receive(self) -> dict[str, str]:
        await self.disconnected.wait()
        return {"type": "websocket.disconnect"}

    async def send_json(self, data: dict) -> None:
        self.messages.append(data)
        self.sent.set()


class WebSocketTest(unittest.IsolatedAsyncioTestCase):
    """空闲连接不轮询 Redis，待发通知可在连接时送达。"""

    async def test_idle_connection_blocks_and_stops_on_disconnect(self) -> None:
        websocket = FakeWebSocket()
        waiting = asyncio.Event()

        async def wait_for_signal(_key: str) -> None:
            waiting.set()
            await asyncio.Future()

        with (
            patch.object(WebSocketUtil, "connect", new_callable=AsyncMock) as connect,
            patch.object(redis_util, "get_websocket_notices", new_callable=AsyncMock) as get_notices,
            patch.object(redis_util, "wait_websocket_signal", side_effect=wait_for_signal) as wait_signal,
        ):
            connect.return_value = True
            get_notices.return_value = {}
            task = asyncio.create_task(websocket_endpoint(websocket, user_id=7))
            try:
                await asyncio.wait_for(waiting.wait(), timeout=1)
                await asyncio.sleep(0.02)
                self.assertEqual(get_notices.await_count, 1)
                wait_signal.assert_awaited_once_with(f"{WEBSOCKET_KEY}7:signal")
            finally:
                websocket.disconnected.set()
                await asyncio.wait_for(task, timeout=1)

    async def test_pending_notice_is_sent_before_waiting(self) -> None:
        websocket = FakeWebSocket()
        payload = {"type": "message", "message": "待发送通知"}
        encoded = orjson.dumps(payload)
        deleted = asyncio.Event()

        async def delete_notice(*_args: object) -> None:
            deleted.set()

        async def wait_for_signal(_key: str) -> None:
            await asyncio.Future()

        with (
            patch.object(WebSocketUtil, "connect", new_callable=AsyncMock) as connect,
            patch.object(redis_util, "get_websocket_notices", new_callable=AsyncMock) as get_notices,
            patch.object(redis_util, "delete_websocket_notice_if_value", new_callable=AsyncMock) as delete,
            patch.object(redis_util, "wait_websocket_signal", new_callable=AsyncMock) as wait_signal,
        ):
            connect.return_value = True
            get_notices.return_value = {b"message": encoded}
            delete.side_effect = delete_notice
            wait_signal.side_effect = wait_for_signal
            task = asyncio.create_task(websocket_endpoint(websocket, user_id=7))
            try:
                await asyncio.wait_for(deleted.wait(), timeout=1)
                self.assertEqual(websocket.messages, [payload])
                delete.assert_awaited_once_with(f"{WEBSOCKET_KEY}7", "message", encoded)
            finally:
                websocket.disconnected.set()
                await asyncio.wait_for(task, timeout=1)

    async def test_send_message_writes_notice_and_signal_together(self) -> None:
        with patch.object(redis_util, "set_websocket_notice", new_callable=AsyncMock) as write:
            await WebSocketUtil.send_message(
                user_id=7,
                message="积分变动",
                notice_type=WebsocketNoticeTypeEnum.POINTS,
            )
            write.assert_awaited_once_with(
                key=f"{WEBSOCKET_KEY}7",
                signal_key=f"{WEBSOCKET_KEY}7:signal",
                field="points",
                value=orjson.dumps({"type": "points", "message": "积分变动"}),
            )

    async def test_signal_wakes_connection_and_delivers_notice(self) -> None:
        websocket = FakeWebSocket()
        deleted = asyncio.Event()
        payload = {"type": "message", "message": "新通知"}
        encoded = orjson.dumps(payload)

        async def delete_notice(*_args: object) -> None:
            deleted.set()

        signal_calls = 0

        async def wait_for_signal(_key: str) -> None:
            nonlocal signal_calls
            signal_calls += 1
            if signal_calls > 1:
                await asyncio.Future()

        with (
            patch.object(WebSocketUtil, "connect", new_callable=AsyncMock) as connect,
            patch.object(redis_util, "get_websocket_notices", new_callable=AsyncMock) as get_notices,
            patch.object(redis_util, "delete_websocket_notice_if_value", new_callable=AsyncMock) as delete,
            patch.object(redis_util, "wait_websocket_signal", new_callable=AsyncMock) as wait_signal,
        ):
            connect.return_value = True
            get_notices.side_effect = [{}, {b"message": encoded}]
            delete.side_effect = delete_notice
            wait_signal.side_effect = wait_for_signal
            task = asyncio.create_task(websocket_endpoint(websocket, user_id=7))
            try:
                await asyncio.wait_for(deleted.wait(), timeout=1)
                self.assertEqual(websocket.messages, [payload])
                self.assertGreaterEqual(wait_signal.await_count, 1)
            finally:
                websocket.disconnected.set()
                await asyncio.wait_for(task, timeout=1)

    async def test_signal_queue_is_bounded_in_one_transaction(self) -> None:
        pipeline = MagicMock()
        pipeline.__aenter__ = AsyncMock(return_value=pipeline)
        pipeline.__aexit__ = AsyncMock(return_value=False)
        pipeline.execute = AsyncMock()
        with patch.object(redis_util.redis_client, "pipeline", return_value=pipeline):
            await redis_util.set_websocket_notice("notice", "signal", "message", b"data")
        self.assertEqual(
            [call[0] for call in pipeline.method_calls],
            ["hset", "lpush", "ltrim", "execute"],
        )
        pipeline.hset.assert_called_once_with(name="notice", key="message", value=b"data")
        pipeline.ltrim.assert_called_once_with("signal", 0, 0)


if __name__ == "__main__":
    unittest.main()
