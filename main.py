import uvicorn
import platform
from argparse import ArgumentParser, Namespace
from application.config.ServerConfig import ServerConfig

# 创建 ArgumentParser 对象
parser: ArgumentParser = ArgumentParser(description="启动ASGI服务器")
# 添加参数
parser.add_argument("start_mode", type=str, choices=["pro", "dev", "debug"],
                    help="启动模式: [pro：生产模式，dev：开发模式（自动重载）]")
# 解析命令行参数
args: Namespace = parser.parse_args()

if __name__ == "__main__":
    # 定义Web API参数
    params: dict = {
        "app": "application:app",
        "host": ServerConfig.host,
        "port": ServerConfig.port,
        "loop": "uvloop" if platform.system() == "Linux" else "asyncio"
    }
    # 开发模式加重载参数
    if args.start_mode == "dev":
        params.update(reload=True)
    elif args.start_mode == "pro":
        params.update(workers=ServerConfig.workers)
    # 启动uvicorn服务器
    uvicorn.run(**params)
