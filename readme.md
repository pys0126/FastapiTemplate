# 🚀🚀🚀 FastAPI 快速开发模板

## Quick Start

此模板基于 FastAPI 开发，基于分层架构的模块化服务设计，提供了基本的功能和结构（基本上开箱即用），可快速开始业务开发。

- 项目使用 `Python>=3.9`。
- 使用 `pyyaml` 读取 `yaml` 配置文件。
- 使用 `pydantic` 构建实体模型。
- 使用 `tortoise-orm[asyncmy]` 构建、操作数据库模型。
- 使用 `redis` 缓存数据。
- 使用 `pyjwt` 构建 JWT 认证。
- 使用 `zmail` 发送邮件。
- 使用 `loguru` 提供日志功能。
- 使用 `uvicorn` 作为项目服务器。
- 使用 `starlette.websockets` 提供 WebSocket 功能。
- 更多依赖项请查看 `requirements.txt` 文件。
- 强烈推荐使用 `venv` 或者 `conda` 虚拟环境，避免环境冲突。

### 一、配置项目

1. 编辑 `config-template.yaml` 配置模板。
2. 将配置信息复制到 `config.yaml`（新建）中。

### 二、运行项目

- 开发模式（自动重载）：`python main.py dev`。
- 生产模式：`python main.py pro`。

**Tips：** 初始超级用户`admin`，密码`admin`。

### 三、各模块说明

- 在 `application/__init__.py` 初始化/注册各插件。
- 在 `application/config` 管理项目配置（数据库、邮件、服务器等）。
- 在 `application/dependency` 定义依赖注入组件（如 `TokenDependency` ）。
- 在 `application/dispatch.py` 处理请求调度。
- 在 `application/exception` 定义自定义异常类（如 `BasicException` ）。
- 在 `application/initial` 提供基础类定义（如 `BaseController`、`BaseEntity`、`BaseEnum`、`BaseModel` ）。
- 在 `application/middleware` 实现中间件功能（如 `PermissionMiddleware`、`ProcessMiddleware` ）。
- 在 `application/service` 实现业务逻辑分层（如 `common` 和 `user` 模块 ）。
- 在 `application/util` 提供各种工具类（邮件、文件、日志、数据库等工具）。

### 四、项目结构说明

```
fastapi-mvc/
├── application/                 # 核心应用目录
│   ├── __init__.py             # 插件初始化/注册
│   ├── config/                 # 配置管理
│   │   ├── DatabaseConfig.py   # 数据库配置
│   │   ├── EmailConfig.py      # 邮件配置
│   │   ├── ServerConfig.py     # 服务器配置
│   │   └── __init__.py
│   ├── dependency/             # 依赖注入
│   │   ├── TokenDependency.py  # Token依赖
│   │   └── __init__.py
│   ├── dispatch.py             # 定义后台任务
│   ├── exception/              # 自定义异常
│   │   ├── BasicException.py   # 基础异常类
│   │   └── __init__.py
│   ├── initial/                # 基础类定义
│   │   ├── BaseController.py   # 基础控制器
│   │   ├── BaseEntity.py       # 基础实体
│   │   ├── BaseEnum.py         # 基础枚举
│   │   ├── BaseModel.py        # 基础模型
│   │   └── __init__.py
│   ├── middleware/             # 中间件
│   │   ├── PermissionMiddleware.py  # 权限控制中间件
│   │   ├── ProcessMiddleware.py     # 请求处理中间件
│   │   └── __init__.py
│   ├── service/                # 业务服务层
│   │   ├── common/             # 通用服务
│   │   │   ├── Controller.py   # 通用控制器
│   │   │   ├── Logic.py        # 通用业务逻辑
│   │   │   ├── Model.py        # 通用模型
│   │   │   └── __init__.py
│   │   ├── user/               # 用户服务
│   │   │   ├── Controller.py   # 用户控制器
│   │   │   ├── Entity.py       # 用户实体
│   │   │   ├── Enum.py         # 用户枚举
│   │   │   ├── Logic.py        # 用户业务逻辑
│   │   │   ├── Model.py        # 用户模型
│   │   │   ├── Util.py         # 用户工具类
│   │   │   └── __init__.py
│   │   └── __init__.py
│   └── util/                   # 全局工具包
│       ├── EmailUtil.py        # 邮件工具
│       ├── FileUtil.py         # 文件工具
│       ├── LogUtil.py          # 日志工具
│       ├── MysqlUtil.py        # MySQL工具
│       ├── RedisUtil.py        # Redis工具
│       ├── ResponseUtil.py     # 响应工具
│       ├── StringUtil.py       # 字符串工具
│       ├── TimeUtil.py         # 时间工具
│       ├── TokenUtil.py        # Token工具
│       ├── WebSocketUtil.py    # WebSocket工具
│       └── __init__.py
├── config-template.yaml        # 配置模板
├── config.yaml                 # 实际配置文件
├── main.py                     # 主入口文件
├── requirements.txt            # 依赖包列表
└── test.py                     # 测试文件
```


### 五、开发规范

- **分层架构**：基于分层架构模式，采用 `Controller`、`Logic`、`Model` 三层架构进行开发，确保代码结构清晰。
- **依赖注入**：使用 `dependency` 模块管理依赖，提高代码可测试性。
- **异常处理**：统一在 `exception` 模块定义自定义异常，保证错误处理一致性。
- **配置管理**：所有配置项应在 `config` 模块中统一管理，避免硬编码。
- **服务模块化**：业务逻辑按功能模块划分到 `service` 目录下，如 `application/service/user` 服务。

### 六、快速开始

1. **创建虚拟环境**：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```


2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```


3. **配置项目**：
   ```bash
   cp config-template.yaml config.yaml  # 编辑 config.yaml 中的配置项
   ```


4. **启动开发模式**：
   ```bash
   python main.py dev
   ```


### 七、部署说明

- **生产环境部署**：使用 `python main.py pro` 启动生产模式
- **反向代理**：建议配合 Nginx 等反向代理服务器使用

### 八、注意事项

- 开发过程中请勿将敏感配置信息提交到版本控制系统
- 遵循 PEP 8 代码规范，保持代码风格统一
- 业务逻辑应集中在 `service` 模块，控制器只负责请求响应处理
- 采用模块化服务结构，新功能开发建议按照 `service` 目录下的模块结构进行扩展