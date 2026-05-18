# 后端架构优化实施计划

## 当前落点

本轮后端重构已经将数据库结构管理从独立的 migrations/Alembic 层收回到应用内部，改为基于现有 ORM 模型直接初始化：

- `app/schema.py` 负责统一注册业务模型与 Agent Runtime 模型
- `initialize_database()` 作为唯一建表入口
- `main.py` 在应用生命周期启动时自动执行 schema 初始化
- `scripts/init_db.py` 提供显式的命令行初始化入口

这样数据库初始化方式与现有分层保持一致：

- `app/models` / `app/agent/models` 定义数据结构
- `app/repositories` / `app/agent/repositories` 承担持久化访问
- `app/services` / `app/agent/services` 承担业务规则
- `app/routers` / `app/agent/router.py` 提供 HTTP 与 SSE 接口

## 调整原因

原先的 migrations 层与当前项目状态存在两类问题：

- schema 变更入口和应用真实启动路径分离，维护成本高
- 仓库中已有脚本和文档对迁移层存在历史耦合，和现在的模型分层不再完全一致

在当前以 SQLite、本地初始化和模型直驱为主的架构下，直接基于 ORM 模型建表更贴近实际运行方式。

## 现在的开发流程

本地初始化数据库：

```bash
uv run python scripts/init_db.py
```

启动后端：

```bash
uvicorn main:app --reload
```

代码校验：

```bash
uv run ruff check .
uv run python -c "import main; print('ok')"
```

## 后续约束

- 新增或调整表结构时，直接修改 `app/models` 或 `app/agent/models`
- 保持 `app/schema.py` 作为统一 schema 初始化入口
- 继续避免数据库外键，关联完整性仍由服务层和仓储层协同保证
- 如果后续出现真正需要版本化升级的数据迁移场景，再单独设计新的迁移机制，而不是恢复旧的 migrations 层
