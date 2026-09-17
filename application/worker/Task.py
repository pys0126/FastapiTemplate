"""ARQ任务函数。"""

from typing import Any

from arq import Retry

from application.config.WorkerConfig import WorkerConfig
from application.service.system.Model import SystemRequestLogModel
from application.util.LogUtil import write_task_log
from application.util.TokenUtil import get_user_id


async def write_request_log(
    ctx: dict[str, Any],
    token: str | None,
    request_body: str | None,
    request_ip: str,
    method: str,
    url_path: str,
    query_params: str | None,
    request_id: str,
) -> None:
    """将请求日志写入数据库。"""
    try:
        user_id = await get_user_id(token=token) if token else None
        await SystemRequestLogModel.get_or_create(
            request_id=request_id,
            defaults={
                "user_id": user_id or None,
                "request_body": request_body,
                "request_ip": request_ip,
                "request_method": method,
                "request_path": url_path,
                "request_query": query_params,
            },
        )
    except Exception as exception:
        write_task_log(
            task_name=write_request_log.__name__,
            status="failed",
            message=(
                f"request_id={request_id}, try={ctx.get('job_try', 1)}, "
                f"error={exception}"
            ),
        )
        raise Retry(defer=WorkerConfig.retry_delay) from exception
