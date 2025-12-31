from fastapi import Request, Response
from starlette.requests import ClientDisconnect
from application.util.StringUtil import random_uuid
from application.dispatch import write_request_log, add_task
from starlette.middleware.base import RequestResponseEndpoint, BaseHTTPMiddleware


class ProcessMiddleware(BaseHTTPMiddleware):
    """请求响应相关中间件类"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        请求响应中间件处理器
        :param request: 请求对象
        :param call_next: 请求处理器
        :return: 响应对象
        """
        # 预处理OPTIONS请求不记录
        if request.method == "OPTIONS":
            return await call_next(request)
        # 生成请求ID
        request_id: str = random_uuid(delimiter=True)
        # 请求处理
        new_request = await ProcessMiddleware.request_dispatch(request=request, request_id=request_id)
        # 响应处理
        response: Response = await call_next(new_request)
        # 请求头添加请求ID
        response.headers.update({"x-request-id": request_id})
        return response

    @staticmethod
    async def request_dispatch(request: Request, request_id: str) -> Request:
        """
        请求处理器
        :param request: 请求对象
        :param request_id: 请求ID
        :return: 请求对象
        """
        # 尝试解码请求体
        try:
            body_data: bytes = await request.body()  # 请求体原数据
            request_body: str = body_data.decode("utf-8") or None
        except UnicodeDecodeError:  # 解码出错了，定义为文件
            request_body: str = "FILE"
        except ClientDisconnect:  # 客户端断开
            return request
        request_headers: dict = dict(request.headers)  # 请求头
        # 获取真实请求IP
        request_ip: str = request_headers.get("x-forwarded-for", request.client.host).split(",")[0]
        if request_ip != "127.0.0.1":
            # 后台写入请求日志
            add_task(write_request_log, request_headers.get("authorization"), request_body, request_ip,
                     request.method, request.url.path, request.query_params, request_id)
        return request
