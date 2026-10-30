---
name: extend-service-module
description: 在本 FastAPI 模板中新增接口、增加业务功能、修改现有 service 代码或扩展业务模块时，遵循项目现有分层、自动注册、响应、鉴权、注释与测试约定；不用于通用 FastAPI 项目。
---

# 本项目 service 功能开发

适用于本仓库新增接口、增加或修改业务功能，以及新建 `application/service/<module>/` 模块。先检查目标模块及相邻实现：已有模块优先在现有文件中扩展；新模块按实际功能选择文件，不必凑齐所有层。当前参照：`common`（Controller、Logic）、`system`（Model、Admin）、`user`（完整业务模块）。保持与用户明确要求及仓库当前代码一致；本说明不是要求复制示例中的所有实现。

## 文件与职责

在 `application/service/<module>/` 下使用小写包名、`__init__.py`，其余文件按功能选用以下**精确文件名**：

| 文件 | 何时创建、放什么 |
| --- | --- |
| `Controller.py` | 提供 HTTP 接口；声明模块级 `router: APIRouter = APIRouter(prefix="/<module>", tags=[...])`，路由只处理参数、依赖、调用 Logic 和响应。 |
| `Logic.py` | 异步业务函数，负责校验、规则、ORM/缓存调用与流程编排；由 Controller 调用，避免把业务逻辑堆在路由里。 |
| `Entity.py` | Pydantic 入参和出参；用 `Field` 等明确约束，需要公共 id/时间字段时继承 `BaseOutEntity`，分页可用 `PagingEntity`。 |
| `Model.py` | Tortoise ORM 模型，继承 `TortoiseBaseModel`；字段写 `description`，`Meta.table` 和 `Meta.table_description` 明确表名与展示名，按需加索引。基类已提供 id、创建/更新时间、`to_dict`、分页查询等。 |
| `Admin.py` | 有后台管理需求才写；`@register(模型类)` 修饰继承 `BaseAdmin` 的管理类，按需配置 `menu_section`、`list_display`、`list_filter`、`search_fields`、`ordering`、只读/表单字段和动作。 |
| `Enum.py`、`Util.py` | 模块内专属枚举、复用的小工具；跨模块通用工具才考虑放进 `application/util/`。 |

同一文件可有多个相关模型/后台管理类，参照 `system/Model.py` 和 `system/Admin.py`。模块之间使用 `application.service.<module>...` 的绝对导入。

## 命名与注释

- 遵循已有命名：模块包小写，层文件为上述 PascalCase 文件名，模型/实体/后台类用 PascalCase，函数和变量用 snake_case；给接口、业务函数、模型字段补充有用的类型标注。
- 对业务函数、模型和后台类用简短中文 docstring 说明用途；参数和返回值需要解释时沿用项目的 `:param 参数名:`、`:return:` 格式（见 `user/Logic.py`、`common/Logic.py`）。接口用清晰的 `summary` 说明用途。简单自明的函数不必为凑格式写空洞注释。
- 行内注释优先解释非显然的规则、状态变化、外部服务调用或兼容原因，参照 `user/Logic.py` 的业务分支与 `common/Logic.py` 的验证码流程；不要逐行复述代码。新增、修改逻辑时同步维护注释，避免注释与行为不符。中文描述与现有模块的术语保持一致。

## 项目集成点

- `application/util/__init__.py` 的 `register_routers`、`register_admin` 扫描 `application/service` 的直接子目录，导入其中的 `Controller.py`、`Admin.py`；Controller 必须暴露名为 `router` 的对象。`application/config/DatabaseConfig.py` 的 `scan_models` 按 `Model.py` 收集 ORM 模型。`application/__init__.py` 在启动时调用这些注册函数，通常无需手动修改总路由或模型列表。
- 上述扫描及 `application/config/__init__.py` 的配置加载依赖当前工作目录是仓库根目录。保持模块为可导入的包；在根目录运行检查/服务，确认新路由和模型确实被发现。
- Controller 采用 `async def`、HTTP 方法装饰器及 `summary`；一般 `return ResponseUtil(data=await Logic.xxx(...)).success()`，无需数据时用 `ResponseUtil().success()`。业务失败在 Logic 中抛 `BasicException(status_code=StatusCodeEnum.XXX)`；需要新业务状态码时在 `application/initial/BaseEnum.py` 定义，不自行拼装不一致的响应体。
- 用户态接口按需要使用 `Depends(verify_token)` 或 `Depends(get_current_user)`（`application/dependency/AuthDependency.py`）；公开接口不强制加鉴权。后台权限与操作继承 `BaseAdmin` 的既有扩展点。
- ORM 查询/写入为异步调用；输出时按接口契约将模型数据转换为 Entity。使用 `response_model` 时要与**实际返回结构**匹配：当前 `user/Controller.py` 的 `/all` 声明为 `UserOut` 却返回分页包装的 `JSONResponse`，不是可复用的规范。
- 配置集中在 `config.yaml` 和 `application/config/`，不硬编码密钥或凭据。生产环境不要靠 `auto_create_table` 自动建表；新增/修改表结构需考虑数据库迁移。不要把 `user/Util.py` 的 SHA1(MD5) 密码实现或 `Admin.py` 的模拟上传地址当作新功能的安全模板。

## 实施与验收

1. 确认需求涉及已有接口/功能还是新模块，以及数据库、后台的哪些部分；选 `common`、`system` 或 `user` 作最近的结构参照，保持职责边界，不生成无用文件。
2. 明确输入校验、输出形状、业务错误、权限、表/字段及后台展示；实现后核对扫描命名、模块导入和路由前缀是否冲突。
3. 为新增或修改的接口在根目录 `tests/` 补充测试，参照 `tests/test_user.py` 的独立路由与业务 mock 写法；需验证鉴权、中间件、真实数据库时另做使用隔离环境的集成测试。先做语法检查，再从项目根目录运行 `python -m unittest discover -s tests -p 'test_*.py' -v`；不要仅凭自动扫描代码推断运行成功。

相关代码入口：`application/service/{common,system,user}/`、`application/util/__init__.py`、`application/config/DatabaseConfig.py`、`application/initial/{BaseModel,BaseEntity,BaseAdmin,BaseEnum}.py`、`application/util/ResponseUtil.py`、`application/dependency/AuthDependency.py`。
