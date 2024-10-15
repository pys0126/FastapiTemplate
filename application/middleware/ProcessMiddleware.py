import json
from typing import Optional
from fastapi import Request, Response
from starlette.responses import AsyncContentStream
from application.util.TokenUtil import get_user_id
from application.util.StringUtil import random_uuid
from starlette.middleware.base import RequestResponseEndpoint, BaseHTTPMiddleware
from application.mapper.SystemMapper import SystemRequestLogMapper, SystemResponseLogMapper


class ProcessMiddleware(BaseHTTPMiddleware):
    """请求响应相关中间件类"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        请求响应中间件处理器
        :param request: 请求对象
        :param call_next: 请求处理器
        :return: 响应对象
        """
        request_id: str = random_uuid(delimiter=True)  # 构造请求ID
        # 请求处理
        new_request: Request = await ProcessMiddleware.request_dispatch(request=request, request_id=request_id)
        # 响应处理
        return await ProcessMiddleware.response_dispatch(response=await call_next(new_request), request_id=request_id)

    @staticmethod
    async def request_dispatch(request: Request, request_id: str) -> Request:
        """
        请求处理器
        :param request: 请求对象
        :param request_id: 请求ID
        :return: 请求对象
        """
        body_data: bytes = await request.body()  # 请求体原数据
        # 尝试解码请求体
        try:
            request_body: str = body_data.decode("u8") or None
        except UnicodeDecodeError:
            request_body: str = "FILE"  # 出错了，定义为文件
        request_headers: dict = dict(request.headers)  # 请求头
        # 获取用户ID
        user_id: Optional[int] = get_user_id(token=request_headers.get("authorization")) or None
        # 插入请求日志
        await SystemRequestLogMapper.insert(data={
            "user_id": user_id,
            "request_body": request_body,
            "request_headers": json.dumps(request_headers, ensure_ascii=False),
            "request_ip": request.client.host,
            "request_method": request.method,
            "request_path": request.url.path,
            "request_query": json.dumps(dict(request.query_params), ensure_ascii=False),
            "request_id": request_id
        })
        return request

    @staticmethod
    async def response_dispatch(response: Response, request_id: str) -> Response:
        """
        响应处理器
        :param response: 响应对象
        :param request_id: 请求ID
        :return: 响应对象
        """
        # 读取响应体
        response_body: list = [item.decode("u8") async for item in response.body_iterator]
        # 重新设置响应体
        response.body_iterator = ProcessMiddleware.response_body_generator(response_body=response_body)
        # 请求头添加请求ID
        response.headers.update({"x-request-id": request_id})
        # 插入响应日志
        await SystemResponseLogMapper.insert(data={
            "request_id": request_id,
            "response_body": response_body[0],
            "response_headers": json.dumps(dict(response.headers), ensure_ascii=False)
        })
        return response

    @staticmethod
    async def response_body_generator(response_body: list) -> AsyncContentStream:
        """
        响应体异步生成器
        :param response_body: 响应体列表
        :return: 响应体生成器
        """
        for item in response_body:
            yield item.encode("u8")
