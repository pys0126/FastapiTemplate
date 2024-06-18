import os
import sys
from application.config.ServerConfig import ServerConfig

# 定义启动命令
command: str = (f"uvicorn application:app --workers {ServerConfig.workers} --host {ServerConfig.host} "
                f"--port {ServerConfig.port}")

if __name__ == "__main__":
    if sys.argv[1] == "dev":
        command = command + " --reload"
    # 启动服务
    os.system(command=command)

