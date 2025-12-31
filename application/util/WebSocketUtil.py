"""
Websocket工具包
"""
from application.initial.BaseEnum import WebsocketNoticeTypeEnum
from application.util.TokenUtil import get_user_id
from application.util.RedisUtil import redis_util
from application.config import WEBSOCKET_KEY
from starlette.websockets import WebSocket
import orjson


class WebSocketUtil:
    """
    Websocket工具类
    """

    @staticmethod
    async def connect(user_id: int, websocket: WebSocket) -> bool:
        """
        创建WS连接
        :param user_id: 用户ID
        :param websocket: Websocket对象
        :return: 连接状态
        """
        # 接受连接
        await websocket.accept()
        print(f"\t用户<{user_id}>连接了Websocket...")
        # 验证Token，不匹配则断开连接
        if user_id == 0 or user_id != await get_user_id(token=websocket.headers.get("Authorization")):
            await websocket.close()
            return False
        return True

    @staticmethod
    async def send_message(user_id: int, message: str,
                           notice_type: WebsocketNoticeTypeEnum = WebsocketNoticeTypeEnum.MESSAGE) -> None:
        """
        发送消息
        :param user_id: 用户ID
        :param message: 消息内容
        :param notice_type: 消息类型
        :return:
        """
        try:
            await redis_util.hash_set(key=f"{WEBSOCKET_KEY}{user_id}", field=notice_type.value,
                                      value=orjson.dumps({"type": notice_type.value, "message": message}).decode("u8"))
        except Exception:
            pass
