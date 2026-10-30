import os
from pathlib import Path
import yaml

# 默认配置与代码同处项目目录；显式路径相对启动时的工作目录解析。
PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]
YAML_PATH: Path = Path(
    os.environ.get("APP_CONFIG", PROJECT_ROOT / "config.yaml")
).expanduser().resolve()

try:
    with YAML_PATH.open(encoding="utf-8") as file:
        YAML_CONTENT = yaml.safe_load(file)
except FileNotFoundError as exc:
    raise FileNotFoundError(
        f"配置文件不存在: {YAML_PATH}；请从 config-template.yaml 创建配置，或设置 APP_CONFIG"
    ) from exc
except yaml.YAMLError as exc:
    raise ValueError(f"配置文件 YAML 格式错误: {YAML_PATH}") from exc

if not isinstance(YAML_CONTENT, dict):
    raise ValueError(f"配置文件必须是 YAML 映射: {YAML_PATH}")

# 项目名称
PROJECT_NAME: str = YAML_CONTENT.get("ProjectName", "TestSystem")

# Redis Key配置
CAPTCHA_KEY: str = "fastapi:captcha:"  # 验证码Key
TOKEN_KEY: str = "fastapi:token:"  # Token Key

WEBSOCKET_KEY: str = "fastapi:webosocket:"  # WebScoket Key
