from application.initial.BaseEnum import WebsocketNoticeTypeEnum
from starlette.websockets import WebSocket, WebSocketDisconnect
from application.util.WebSocketUtil import WebSocketUtil
from application.util.ResponseUtil import ResponseUtil
from application.util.RedisUtil import redis_util
from starlette.responses import JSONResponse
from application.config import WEBSOCKET_KEY
from datetime import datetime
from fastapi import APIRouter
from typing import Optional
import orjson

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
    if await WebSocketUtil.connect(user_id=user_id, websocket=websocket):
        try:
            while True:
                # 遍历通知类型枚举
                for notice_type in WebsocketNoticeTypeEnum:
                    # 监听当前通知类型Redis缓存的消息
                    message: Optional[str] = await redis_util.hash_get(key=f"{WEBSOCKET_KEY}{user_id}",
                                                                       field=notice_type.value)
                    # 如果没有消息，则进行下一个循环
                    if not message: continue
                    # 发送WS消息
                    await websocket.send_json(data=orjson.loads(message))
                    print(f"{str(datetime.now())}\t用户<{user_id}>推送Websocket消息：{message.decode('u8')}！")
                    # 清理当前通知类型Redis缓存
                    await redis_util.hash_del(key=f"{WEBSOCKET_KEY}{user_id}", fields=[notice_type.value])
        except WebSocketDisconnect:
            print(f"\t用户<{user_id}>断开了Websocket连接！")
