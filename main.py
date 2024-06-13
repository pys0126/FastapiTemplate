import os
from application.config.ServerConfig import ServerConfig

command: str = (f"uvicorn application:app --workers {ServerConfig.workers} --host {ServerConfig.host} "
                f"--port {ServerConfig.port}")

if __name__ == "__main__":
    # 启动服务
    os.system(command=command)

