# FastAPI快速开发模板

## Quck Start

此模板基于FastAPI开发，提供了基本的功能和结构（基本上开箱即用），可快速开始开发。依赖项请查看`requirements.txt`文件。

- 项目使用`Python>=3.9`。
- 强烈推荐使用`venv`或者`conda`虚拟环境，避免环境冲突。

### 一、配置项目

1. 编辑`config-template.yaml`配置模板。
2. 将配置信息复制到`config.yaml`（新建）中。

### 二、运行项目

- 开发模式（自动重载）：`python main.py dev`。
- 生产模式：`python main.py pro`。

### 三、各模块说明

- 在`application/__init__.py`初始化/注册各插件。
- 在`application/controller`自定义控制器。
- 在`application/model`自定义模型。
- 在`application/mapper`自定义DAO。
- 在`application/logic`自定义业务逻辑。
- 在`application/entity`自定义实体。
- 在`application/dependency`自定义依赖。
- 在`application/config`自定义配置。
- 在`application/enumeration`自定义枚举类型。
- 在`application/util`自定义工具类。
- 在`application/exception`自定义异常类。
- 在`application/middleware`自定义中间件。

### 四、项目结构说明

```
fastapi-mvc/
├── application/                 # 核心应用目录
│   ├── __init__.py             # 插件初始化/注册
│   ├── controller/             # 控制器层
│   ├── model/                  # 数据模型层
│   ├── mapper/                 # 数据访问对象(DAO)
│   ├── logic/                  # 业务逻辑层
│   ├── entity/                 # 实体类
│   ├── dependency/             # 依赖注入
│   ├── config/                 # 配置管理
│   ├── enumeration/            # 枚举类型
│   ├── util/                   # 工具类
│   ├── exception/              # 自定义异常
│   └── middleware/             # 中间件
├── config-template.yaml        # 配置模板
├── config.yaml                 # 实际配置文件
├── main.py                     # 主入口文件
└── readme.md                   # 项目说明文档
```


### 五、开发规范

- **分层架构**：严格按照MVC模式进行分层开发，确保代码结构清晰。
- **依赖注入**：使用`dependency`模块管理依赖，提高代码可测试性。
- **异常处理**：统一在`exception`模块定义自定义异常，保证错误处理一致性。
- **配置管理**：所有配置项应在`config`模块中统一管理，避免硬编码。

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
   cp config-template.yaml config.yaml
   # 编辑 config.yaml 中的配置项
   ```


4. **启动开发模式**：
   ```bash
   python main.py dev
   ```


### 七、部署说明

- **生产环境部署**：使用`python main.py pro`启动生产模式
- **反向代理**：建议配合Nginx等反向代理服务器使用

### 八、注意事项

- 开发过程中请勿将敏感配置信息提交到版本控制系统
- 遵循PEP 8代码规范，保持代码风格统一
- 业务逻辑应集中在`logic`模块，控制器只负责请求响应处理
- 数据库操作应通过`mapper`层进行，避免直接在控制器中操作数据库