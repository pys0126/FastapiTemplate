import asyncio

import orjson
from fastapi import APIRouter
from starlette.responses import JSONResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from application.config import WEBSOCKET_KEY
from application.initial.BaseEnum import WebsocketNoticeTypeEnum
from application.util.RedisUtil import redis_util
from application.util.ResponseUtil import ResponseUtil
from application.util.WebSocketUtil import WebSocketUtil

router: APIRouter = APIRouter(prefix="", tags=["根路径"])


@router.get("/")
@router.get("/index")
async def root() -> JSONResponse:
    """
    主页/根路径，测试API是否正常
    """
    return ResponseUtil().success()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int) -> None:
    """
    WS接口
    :return:
    """
    if not await WebSocketUtil.connect(user_id=user_id, websocket=websocket):
        return
    key = f"{WEBSOCKET_KEY}{user_id}"
    signal_key = f"{key}:signal"
    disconnect_task = asyncio.create_task(_wait_for_disconnect(websocket))
    signal_task: asyncio.Task[None] | None = None
    try:
        while not disconnect_task.done():
            # 建立连接时先处理历史通知，之后只在新通知到达时读取 Redis。
            notices = await redis_util.get_websocket_notices(key)
            for notice_type in WebsocketNoticeTypeEnum:
                message = notices.get(notice_type.value.encode("utf-8"))
                if message is None:
                    continue
                await websocket.send_json(data=orjson.loads(message))
                await redis_util.delete_websocket_notice_if_value(
                    key, notice_type.value, message
                )
            if disconnect_task.done():
                break
            signal_task = asyncio.create_task(
                redis_util.wait_websocket_signal(signal_key)
            )
            done, _ = await asyncio.wait(
                (disconnect_task, signal_task),
                return_when=asyncio.FIRST_COMPLETED,
            )
            if disconnect_task in done:
                disconnect_task.result()
                break
            signal_task.result()
            signal_task = None
    except WebSocketDisconnect:
        pass
    finally:
        for task in (signal_task, disconnect_task):
            if task is not None and not task.done():
                task.cancel()
        await asyncio.gather(
            *(task for task in (signal_task, disconnect_task) if task is not None),
            return_exceptions=True,
        )


async def _wait_for_disconnect(websocket: WebSocket) -> None:
    """持续接收客户端事件，以便在空闲时及时结束 Redis 阻塞等待。"""
    while (await websocket.receive())["type"] != "websocket.disconnect":
        pass
