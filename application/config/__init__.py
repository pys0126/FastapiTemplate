import yaml
import os

# yaml文件路径
YAML_PATH: str = os.path.join(os.getcwd(), "config.yaml")

# 读取yaml文件
with open(YAML_PATH, mode="r", encoding="u8") as file:
    YAML_CONTENT: dict = yaml.load(file, Loader=yaml.FullLoader)

# 项目名称
PROJECT_NAME: str = YAML_CONTENT.get("ProjectName", "TestSystem")

# Redis Key配置
CAPTCHA_KEY: str = "fastapi:captcha:"  # 验证码Key
TOKEN_KEY: str = "fastapi:token:"  # Token Key

WEBSOCKET_KEY: str = "fastapi:webosocket:"  # WebScoket Key