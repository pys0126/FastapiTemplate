from typing import Optional, Union
from collections.abc import Iterable
from redis.asyncio import Redis, ConnectionPool
from application.config.DatabaseConfig import RedisConfig


_HASH_DELETE_IF_VALUE = """
if redis.call('HGET', KEYS[1], ARGV[1]) == ARGV[2] then
    return redis.call('HDEL', KEYS[1], ARGV[1])
end
return 0
"""


class RedisUtil:
    def __init__(self) -> None:
        self.redis_pool: ConnectionPool = ConnectionPool(host=RedisConfig.host, port=RedisConfig.port,
                                                         password=RedisConfig.password, db=RedisConfig.db)
        self.redis_client: Redis = Redis(connection_pool=self.redis_pool)

    async def set_value(self, key: str, value: Union[str, bytes], ex: Optional[int] = None) -> None:
        """
        设置缓存值
        :param key: 键名
        :param value: 值
        :param ex: 存储时间，单位秒
        :return:
        """
        await self.redis_client.set(name=key, value=value, ex=ex)

    async def set_list_values(self, key: str, values: Iterable) -> None:
        """
        设置List的缓存值
        :param key: 键名
        :param values: 值列表
        :return:
        """
        await self.redis_client.rpush(key, *values)

    async def get_list_values(self, key: str, start: int = 0, end: int = -1) -> list:
        """
        获取List的缓存值列表
        :param key: 键名
        :param start: 起始索引（包含）
        :param end: 结束索引（包含）
        :return: 值列表
        """
        return [item.decode("utf-8") for item in await self.redis_client.lrange(key, start, end)]

    async def get_list_value(self, key: str, index: int = 0) -> str:
        """
        获取List的缓存值
        :param key: 键名
        :param index: 元素索引
        :return: 值
        """
        value: Optional[str] = await self.redis_client.lindex(key, index)
        return value if value else None

    async def pop_list_value(self, key: str) -> Union[str, list]:
        """
        删除队列中队首元素并获取其值
        :param key: 键名
        :return: 元素值
        """
        value: Union[str, list] = await self.redis_client.lpop(key)
        return value if value else None

    async def delete_list_value(self, key: str, value: str, count: int = 0) -> None:
        """
        删除队列中指定元素
        :param key: 键名
        :param value: 指定元素值
        :param count: 状态值
            # count > 0: 从表头开始向表尾搜索，移除与element相等的元素，数量为count
            # count < 0: 从表尾开始向表头搜索，移除与element相等的元素，数量为count的绝对值
            # count = 0: 移除表中所有与element相等的元素
        :return:
        """
        await self.redis_client.lrem(key, count, value)

    async def hash_set(self, key: str, field: str, value: str) -> None:
        """
        设置哈希表值
        :param key: 键名
        :param field: 字段名
        :param value: 字段值
        :return:
        """
        await self.redis_client.hset(name=key, key=field, value=value)

    async def hash_get(self, key: str, field: str) -> Optional[str]:
        """
        获取哈希表值
        :param key: 键名
        :param field: 字段名
        :return: 字段值
        """
        return await self.redis_client.hget(name=key, key=field)

    async def hash_del(self, key: str, fields: list) -> None:
        """
        删除哈希表字段
        :param key: 键名
        :param fields: 字段名列表
        :return:
        """
        await self.redis_client.hdel(key, *fields)

    async def set_websocket_notice(
        self, key: str, signal_key: str, field: str, value: bytes
    ) -> None:
        """原子写入最新通知并唤醒等待的 WebSocket，信号队列最多保留一项。"""
        async with self.redis_client.pipeline(transaction=True) as pipeline:
            pipeline.hset(name=key, key=field, value=value)
            pipeline.lpush(signal_key, "1")
            pipeline.ltrim(signal_key, 0, 0)
            await pipeline.execute()

    async def get_websocket_notices(self, key: str) -> dict[bytes, bytes]:
        """读取用户当前待发送的通知。"""
        return await self.redis_client.hgetall(key)

    async def wait_websocket_signal(self, signal_key: str) -> None:
        """阻塞等待新通知；连接断开时由调用方取消等待。"""
        await self.redis_client.blpop(signal_key, timeout=0)

    async def delete_websocket_notice_if_value(
        self, key: str, field: str, value: bytes
    ) -> None:
        """只清除已发送的版本，避免覆盖期间删掉更新的通知。"""
        await self.redis_client.eval(_HASH_DELETE_IF_VALUE, 1, key, field, value)

    async def get_value(self, key: str) -> Optional[str]:
        """
        获取缓存值
        :param key: 键名
        :return: 值
        """
        try:
            return (await self.redis_client.get(name=key)).decode("utf-8")
        except AttributeError:
            return None

    async def get_keys(self, pattern="*") -> list:
        """
        获取所有键名
        :param pattern: 键名正则
        :return: 键名列表
        """
        return [key.decode("utf-8") for key in await self.redis_client.keys(pattern=pattern)]

    async def delete_by_key(self, key: str) -> None:
        """
        根据Key删除值
        :param key: 键名
        :return:
        """
        await self.redis_client.delete(key)

    async def clean(self) -> None:
        """
        清理资源
        :return:
        """
        await self.redis_client.close()


# Redis单例客户端
redis_util: RedisUtil = RedisUtil()
