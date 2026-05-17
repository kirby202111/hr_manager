# 后端架构优化实施计划

## 目标

本次优化把后端从“仓储各自开会话、启动时自动建表、HTTP 异常散落在业务层”的形态，调整为更清晰的分层架构：

- 路由层负责 HTTP 入参、依赖注入和响应模型。
- 服务层负责业务规则、关联校验和领域异常。
- 仓储层负责 SQLAlchemy 查询，并接收调用方传入的数据库会话。
- 数据库结构由 Alembic 管理。
- Agent 资源只在应用生命周期内创建一次，从 `app.state` 获取。

## 不使用外键

项目明确不使用数据库外键。所有 `department_id`、`employee_id`、`skill_id`、`project_id`、`requirement_id`、`memory_id` 都保留为普通整数字段。

关联完整性由服务层校验，例如：

- 创建员工时校验部门是否存在。
- 创建考勤、请假、薪资时校验员工是否存在。
- 创建项目成员、工时、技能需求时校验对应项目、员工、技能目录是否存在。

数据库层只承担唯一约束和索引职责，不创建 `ForeignKey` 约束。

## 已实施改造

- `app/database.py`
  - 增加 `get_db()`，用于 FastAPI 请求级 session。
  - 增加 `session_scope()`，用于脚本、Agent skills 等非 HTTP 场景。
  - 增加 `db_session()`，让仓储函数兼容显式 session 和旧式直接调用。

- `app/errors.py`
  - 增加 `AppError`、`NotFoundError`、`ConflictError`、`ValidationError`。
  - 增加统一异常处理器，路由返回稳定的 `detail` 和 `error_code`。

- 仓储层
  - 主要 repository 均支持传入 `Session`。
  - 写操作使用 `flush()` 和 `refresh()`，由外层请求或 `session_scope()` 统一提交。

- 服务层
  - 核心业务服务改为接收 `Session`。
  - 业务校验抛领域异常，不再直接依赖 HTTP 异常。

- Agent
  - 移除 `app.agent.router` import 时创建的全局 Agent。
  - `main.py` 的 lifespan 创建唯一 Agent、SkillRegistry、HistoryStore。
  - Agent 接口从 `request.app.state` 获取运行时实例。

- 迁移
  - 新增 Alembic 配置和 baseline migration。
  - baseline migration 只创建表、列、唯一约束和索引，不包含任何外键。
  - `main.py` 停止启动时 `create_all()` 和手写 schema migration。

## 约束与索引

已加入的关键约束：

- 部门名唯一：`uq_departments_name`
- 员工同日考勤唯一：`uq_attendance_employee_date`
- 员工同月薪资唯一：`uq_payrolls_employee_month`
- 员工同一技能名唯一：`uq_employee_skills_employee_skill_name`
- 项目同一技能需求唯一：`uq_project_requirements_project_skill`
- 项目成员不重复：`uq_project_members_project_employee`

已加入的关键索引覆盖常用查询：

- 员工按部门查询。
- 考勤按员工和日期查询。
- 请假按员工、状态和日期范围查询。
- 薪资按员工和月份查询。
- 项目、项目成员、项目需求、项目工时的列表与聚合查询。

## 开发流程

本地数据库初始化：

```bash
alembic upgrade head
```

验证：

```bash
ruff check .
```

## 后续注意事项

- 新增关联字段时仍然不要使用数据库外键。
- 新增业务写操作时，优先让 router 注入 `Session`，service 和 repository 继续向下传递。
- 新增 migration 前检查是否意外生成 `ForeignKeyConstraint`。
- 如果生产库已有重复数据，需要先清理后再应用唯一约束。
