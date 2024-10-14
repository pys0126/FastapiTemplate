import uvicorn
from application import app
from argparse import ArgumentParser, Namespace
from application.config.ServerConfig import ServerConfig

# 创建 ArgumentParser 对象
parser: ArgumentParser = ArgumentParser(description="启动ASGI服务器")
# 添加参数
parser.add_argument("start_mode", type=str, choices=["pro", "dev", "debug"],
                    help="启动模式: [pro：生产模式，dev：开发模式（自动重载），debug：调试模式（IDE可调试）]")
# 解析命令行参数
args: Namespace = parser.parse_args()

if __name__ == "__main__":
    params: dict = {
        "app": app,
        "host": ServerConfig.host,
        "port": ServerConfig.port
    }
    if args.start_mode == "dev":
        params.update(app="application:app")
        params.update(reload=True)
    elif args.start_mode == "pro":
        params.update(app="application:app")
        params.update(workers=ServerConfig.workers)
    # 启动ASGI服务器
    uvicorn.run(**params)


