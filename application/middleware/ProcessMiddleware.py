from arq.connections import ArqRedis
from fastapi import Request, Response
from starlette.background import BackgroundTask, BackgroundTasks
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import ClientDisconnect
from application.config.WorkerConfig import WorkerConfig
from application.util.StringUtil import random_uuid
from application.worker import enqueue_task

# 跳过、允许的请求方法（除开GET）
SKIP_LOG_METHODS: set[str] = {"OPTIONS"}
BODY_LOG_METHODS: set[str] = {"POST", "PUT", "PATCH"}
# 允许的请求体类型
BODY_LOG_CONTENT_TYPES: tuple[str, ...] = (
    "application/json",
    "application/x-www-form-urlencoded",
    "text/",
)
# 允许的请求体大小（字节）
MAX_LOG_BODY_SIZE: int = 4096


class ProcessMiddleware(BaseHTTPMiddleware):
    """请求响应相关中间件类"""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        请求响应中间件处理器
        :param request: 请求对象
        :param call_next: 请求处理器
        :return: 响应对象
        """
        # 预处理OPTIONS请求、admin路径不记录
        if request.method in SKIP_LOG_METHODS or "admin" in request.url.path:
            return await call_next(request)
        # 生成请求ID
        request_id: str = random_uuid(delimiter=True)
        # 请求处理
        log_task = await ProcessMiddleware.request_dispatch(
            request=request, request_id=request_id
        )
        try:
            response: Response = await call_next(request)
        except Exception:
            # 异常请求没有正常响应，仍保留原有的日志入队行为。
            if log_task is not None:
                await log_task()
            raise
        # 请求头添加请求ID
        response.headers.update({"x-request-id": request_id})
        if log_task is not None:
            # 在响应发送完成后入队，不让 Redis 往返阻塞普通请求返回。
            if response.background is None:
                response.background = log_task
            else:
                response.background = BackgroundTasks(
                    [log_task, response.background]
                )
        return response

    @staticmethod
    async def request_dispatch(
        request: Request, request_id: str
    ) -> BackgroundTask | None:
        """
        请求处理器
        :param request: 请求对象
        :param request_id: 请求ID
        :return: 响应发送后执行的日志任务；未配置队列时不创建
        """
        task_pool: ArqRedis | None = getattr(request.app.state, "task_pool", None)
        if task_pool is None:
            return None
        # 获取真实请求IP
        request_ip: str = ProcessMiddleware.get_client_ip(request=request)
        request_body: str | None = await ProcessMiddleware.get_request_body(
            request=request
        )
        # 响应发送后只写入 Redis 队列，数据库操作由独立 ARQ worker 执行。
        return BackgroundTask(
            enqueue_task,
            task_pool,
            "write_request_log",
            token=request.headers.get("authorization"),
            request_body=request_body,
            request_ip=request_ip,
            method=request.method,
            url_path=request.url.path,
            query_params=request.url.query or None,
            request_id=request_id,
            _job_id=f"request-log:{request_id}",
            _expires=WorkerConfig.job_expires,
        )

    @staticmethod
    def get_client_ip(request: Request) -> str:
        """
        获取客户端IP
        :param request: 请求对象
        :return:
        """
        forwarded_for: str | None = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",", 1)[0].strip()
        if request.client is None:
            return ""
        return request.client.host

    @staticmethod
    async def get_request_body(request: Request) -> str | None:
        """
        获取用于日志记录的请求体。只记录小体积文本请求，避免大请求和文件上传阻塞主链路。
        :param request: 请求对象
        :return:
        """
        if request.method not in BODY_LOG_METHODS:
            return None
        content_length: str | None = request.headers.get("content-length")
        if content_length is None:
            return None
        try:
            body_size: int = int(content_length)
        except ValueError:
            return None
        if body_size > MAX_LOG_BODY_SIZE:
            return "BODY_TOO_LARGE"
        content_type: str = request.headers.get("content-type", "").lower()
        if not content_type.startswith(BODY_LOG_CONTENT_TYPES):
            return "FILE" if content_type.startswith("multipart/") else None
        try:
            body_data: bytes = await request.body()
            return body_data.decode("utf-8") or None
        except UnicodeDecodeError:
            return "FILE"
        except (ClientDisconnect, ValueError):
            return None
