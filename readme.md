# 基于FastApi的MVC模式开发模板

## 简要说明

- 项目使用`Python>=3.9`。
 
- 强烈推荐使用`venv`或者`conda`虚拟环境，避免环境冲突。

- 整个项目应关注于`application`目录下的内容，其他模块为辅助工具。

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
- 在`application/logic`自定义业务逻辑。
- 在`application/entity`自定义实体。
- 在`application/dependency`自定义依赖。
- 在`application/config`自定义配置。 
- 在`application/enumeration`自定义枚举类型。 
- 在`application/util`自定义工具类。 
- 在`application/exception`自定义异常类。 
- 在`application/middleware`自定义中间件。