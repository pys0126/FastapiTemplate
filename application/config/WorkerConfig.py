"""
ARQ后台任务配置
"""

from application.config import YAML_CONTENT


class WorkerConfig:
    """ARQ后台任务配置。"""

    WORKER_CONFIG: dict = YAML_CONTENT.get("WorkerConfig", {})

    queue_name: str = WORKER_CONFIG.get("queue_name", "arq:queue:fastapi-template")
    max_jobs: int = max(1, int(WORKER_CONFIG.get("max_jobs", 5)))
    job_timeout: float = max(0.1, float(WORKER_CONFIG.get("job_timeout", 10)))
    max_tries: int = max(1, int(WORKER_CONFIG.get("max_tries", 3)))
    retry_delay: float = max(0.1, float(WORKER_CONFIG.get("retry_delay", 2)))
    job_expires: int = max(1, int(WORKER_CONFIG.get("job_expires", 60)))
    enqueue_timeout: float = max(0.1, float(WORKER_CONFIG.get("enqueue_timeout", 0.5)))
    shutdown_timeout: int = max(1, int(WORKER_CONFIG.get("shutdown_timeout", 10)))
