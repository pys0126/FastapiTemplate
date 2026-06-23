# 🚀🚀🚀 FastAPI 快速开发模板

基于 FastAPI 的分层架构快速开发模板，提供开箱即用的基础功能与模块化服务结构，可快速进入业务开发。

## ✨ 特性

- **分层架构**：`Controller` → `Logic` → `Model` 三层结构，职责清晰。
- **自动注册**：路由、中间件、异常均按目录约定自动注册，新增模块零配置接入。
- **JWT 认证**：基于 `pyjwt` 与依赖注入实现，开箱即用。
- **异步 ORM**：`tortoise-orm` + `asyncmy` 操作 MySQL，支持自动建表。
- **Redis 缓存**：封装 Token、验证码、WebSocket 消息等缓存场景。
- **WebSocket**：基于 `Redis` 的跨进程消息推送。
- **统一响应与异常**：`ResponseUtil` 统一响应格式，自定义异常全局接管。
- **后台任务**：`dispatch` 模块提供带日志与异常捕获的异步任务管理。
- **日志体系**：`loguru` 输出应用日志，请求日志落库可追溯。

## 🧰 技术栈

| 分类       | 选型                          |
| ---------- | ----------------------------- |
| Web 框架   | FastAPI + Uvicorn（uvloop）   |
| 数据校验   | Pydantic                      |
| ORM        | tortoise-orm + asyncmy (MySQL)|
| 缓存       | redis                         |
| 认证       | pyjwt                         |
| 邮件       | zmail                         |
| 配置       | pyyaml                        |
| 日志       | loguru                        |
| WebSocket  | starlette.websockets          |

> 完整依赖见 [`requirements.txt`](./requirements.txt)。

## 📋 环境要求

- Python `>=3.9`
- MySQL（推荐 5.7+ / 8.0）
- Redis（推荐 6.0+）
- 强烈推荐使用 `venv` 或 `conda` 虚拟环境，避免环境冲突。

## 🚀 快速开始

### 1. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate      # Linux / macOS
# venv\Scripts\activate       # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置项目

由模板复制生成实际配置文件（`config.yaml` 已被 `.gitignore` 忽略，不会提交敏感信息）：

```bash
cp config-template.yaml config.yaml
```

按需编辑 `config.yaml` 中的服务器、数据库、Redis、邮箱等配置项。

### 4. 启动服务

```bash
python main.py dev   # 开发模式（自动重载）
python main.py pro    # 生产模式（多进程）
python main.py debug  # 调试模式
```

> **初始超级用户**：用户名 `admin`，密码 `admin`（首次启动且用户表为空时自动创建）。

## 📦 部署说明

### 直接运行

生产环境使用多进程模式启动：

```bash
python main.py pro
```

### 使用 service.sh（推荐）

项目内置 [`service.sh`](./service.sh) 进程管理脚本，提供 `start` / `stop` / `kill` / `restart` / `status` 命令：

```bash
./service.sh start    # 启动（生产模式，后台运行）
./service.sh stop     # 优雅停止
./service.sh kill     # 强制终止
./service.sh restart  # 重启
./service.sh status   # 查看运行状态
```

脚本支持通过环境变量自定义 Python 路径、入口文件、PID 与日志路径：

```bash
PYTHON_BIN=/path/to/python LOG_DIR=/var/log/fastapi ./service.sh start
```

### 反向代理

建议配合 Nginx/Caddy 等反向代理服务器使用，负责 TLS 终止、负载均衡与静态资源。

## 📂 项目结构

```
fastapi-template/
├── application/                      # 核心应用目录
│   ├── __init__.py                   # FastAPI 实例创建与各组件注册
│   ├── config/                       # 配置管理
│   │   ├── DatabaseConfig.py         # 数据库配置（MySQL / Redis）
│   │   ├── EmailConfig.py            # 邮件配置
│   │   ├── ServerConfig.py           # 服务器配置（含 CORS）
│   │   └── __init__.py               # 读取 config.yaml，导出全局配置与 Redis Key
│   ├── dependency/                   # 依赖注入
│   │   └── AuthDependency.py         # Token 解析 / 校验 / 获取当前用户
│   ├── dispatch.py                   # 后台任务与请求日志落库
│   ├── exception/                    # 自定义异常
│   │   └── BasicException.py         # 基础异常类与状态码枚举
│   ├── initial/                      # 基础类定义
│   │   ├── BaseController.py         # 基础控制器（根路由 / WebSocket）
│   │   ├── BaseEntity.py             # 基础实体
│   │   ├── BaseEnum.py               # 基础枚举
│   │   └── BaseModel.py              # 基础 ORM 模型
│   ├── middleware/                   # 中间件
│   │   ├── PermissionMiddleware.py   # 权限控制
│   │   └── ProcessMiddleware.py      # 请求处理 / 日志
│   ├── service/                      # 业务服务层（按模块划分）
│   │   ├── common/                   # 通用服务
│   │   │   ├── Controller.py
│   │   │   ├── Logic.py
│   │   │   └── Model.py
│   │   └── user/                     # 用户服务
│   │       ├── Controller.py         # 路由与请求处理
│   │       ├── Entity.py             # 出入参实体
│   │       ├── Enum.py               # 业务枚举
│   │       ├── Logic.py              # 业务逻辑
│   │       ├── Model.py              # ORM 模型
│   │       └── Util.py               # 用户工具（密码加密等）
│   └── util/                         # 全局工具包
│       ├── EmailUtil.py              # 邮件
│       ├── FileUtil.py               # 文件
│       ├── LogUtil.py                # 日志
│       ├── MysqlUtil.py              # MySQL / ORM 配置
│       ├── RedisUtil.py              # Redis
│       ├── ResponseUtil.py           # 统一响应
│       ├── StringUtil.py             # 字符串校验
│       ├── TimeUtil.py               # 时间
│       ├── TokenUtil.py              # Token 生成 / 校验
│       └── WebSocketUtil.py          # WebSocket 管理
├── config-template.yaml              # 配置模板
├── config.yaml                       # 实际配置（需自行创建，已忽略提交）
├── service.sh                        # 进程管理脚本
├── main.py                           # 主入口（启动 Uvicorn）
├── requirements.txt                  # 依赖列表
└── LICENSE                           # Apache-2.0
```

## 🧩 模块说明

- **初始化注册**：`application/__init__.py` 创建 FastAPI 实例，注册 Tortoise ORM、中间件、路由、异常。
- **配置管理**：`application/config` 统一管理数据库、邮件、服务器等配置，避免硬编码。
- **依赖注入**：`application/dependency` 提供鉴权相关依赖，如 `verify_token`、`get_current_user`。
- **请求调度**：`application/dispatch.py` 提供后台任务执行（带日志与异常捕获）及请求日志落库。
- **自定义异常**：`application/exception` 统一定义异常类与全局处理器，保证错误响应一致。
- **基础类**：`application/initial` 提供 `BaseController`、`BaseEntity`、`BaseEnum`、`BaseModel` 等基类。
- **中间件**：`application/middleware` 实现 `PermissionMiddleware`、`ProcessMiddleware`。
- **业务服务**：`application/service` 按功能模块划分，如 `common`（通用）、`user`（用户）。
- **工具包**：`application/util` 提供邮件、文件、日志、数据库、Redis、Token 等工具方法。

## 📐 开发规范

- **分层架构**：采用 `Controller`、`Logic`、`Model` 三层架构，控制器仅处理请求响应，业务逻辑集中在 `Logic`。
- **模块化扩展**：新增业务模块时，在 `application/service/` 下按目录结构新建模块，路由/中间件/异常将自动注册。
- **依赖注入**：通过 `dependency` 模块管理公共依赖，提升可测试性。
- **异常处理**：自定义异常统一在 `exception` 模块定义，由全局处理器接管。
- **配置管理**：所有配置项在 `config` 模块统一管理，禁止硬编码。
- **代码风格**：遵循 PEP 8，保持风格统一。

## 📄 接口示例

启动后访问根路径验证服务：

```bash
curl http://127.0.0.1:7878/
```

用户登录获取 Token：

```bash
curl -X POST http://127.0.0.1:7878/user/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

> 接口文档（`/docs`、`/redoc`）默认关闭，如需开启请修改 `application/__init__.py` 中的 `docs_url` / `redoc_url`。

## ⚠️ 注意事项

- 请勿将 `config.yaml` 等含敏感信息的文件提交到版本控制系统（已在 `.gitignore` 中忽略）。
- 业务逻辑应集中在 `service` 模块的 `Logic` 层，控制器只负责请求与响应处理。
- 新功能开发建议遵循 `application/service/` 下的模块结构进行扩展。

## 📜 开源协议

本项目基于 [Apache License 2.0](./LICENSE) 开源。
