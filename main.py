from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from typing import Any


def create_parser() -> ArgumentParser:
    """创建启动参数解析器。"""
    parser = ArgumentParser(description="启动Web服务或ARQ后台任务进程")
    parser.add_argument(
        "start_mode",
        choices=["pro", "dev", "debug", "worker"],
        help=(
            "启动模式: pro=生产Web服务, dev=热重载Web服务, "
            "debug=单进程Web服务, worker=ARQ后台任务"
        ),
    )
    return parser


def run_web(start_mode: str) -> None:
    """启动Uvicorn Web服务。"""
    import uvicorn

    from application.config import PROJECT_ROOT
    from application.config.ServerConfig import ServerConfig

    params: dict[str, Any] = {
        "app": "application:app",
        "host": ServerConfig.host,
        "port": ServerConfig.port,
        "loop": "auto",  # 有 uvloop 时自动启用，缺失时退回 asyncio。
    }
    if start_mode == "dev":
        params.update(reload=True, reload_dirs=[str(PROJECT_ROOT)])
    elif start_mode == "pro":
        params.update(workers=ServerConfig.workers)
    uvicorn.run(**params)


def main(argv: Sequence[str] | None = None) -> None:
    """根据启动模式运行Web服务或ARQ worker。"""
    args: Namespace = create_parser().parse_args(argv)
    if args.start_mode == "worker":
        from arq.worker import run_worker

        from application.worker.Worker import WorkerSettings

        run_worker(WorkerSettings)
        return
    run_web(start_mode=args.start_mode)


if __name__ == "__main__":
    main()
