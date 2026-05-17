# Workforce Ops

Workforce Ops 是一个面向制造业现场的人力运营系统。当前仓库以 FastAPI 后端为主，配有一个 Vue 3 聊天前端，以及一套可调用业务能力的 Agent。它覆盖了人员、组织、技能、资质、生产现场、排班、考勤、薪资和项目协同等模块。

这份 README 按当前代码结构更新，重点反映现在已经存在的分层、接口和运行方式。

## 当前形态

- 后端是一个 `FastAPI` 应用，入口在 `main.py`，应用版本是 `2.0.0`
- 前端是一个单路由的聊天界面，位于 `frontend/`，主要消费 Agent 聊天和技能相关接口
- 数据访问层已经按领域拆成包，并进一步拆到实体模块，例如 `app/repositories/shopfloor/production_line.py`
- 服务层直接依赖实体级 repository；领域包和顶层 `app/repositories/__init__.py` 仍保留聚合导出
- Agent 在应用启动时初始化，支持同步问答、SSE 流式问答、会话历史和技能开关
- 默认数据库是本地 SQLite：`sqlite:///./data/hr_system.db`

## 技术栈

### 后端

- Python 3.13
- FastAPI
- SQLAlchemy 2
- Alembic
- Pydantic Settings
- Uvicorn
- OpenAI SDK
- SSE Starlette
- ChromaDB

### 前端

- Vue 3
- Vite
- TypeScript
- Element Plus
- Pinia
- Axios

## 代码结构

```text
.
├─ app
│  ├─ agent/            # Agent 运行时、路由、技能注册、会话历史
│  ├─ knowledge_base/   # 知识库接入与检索
│  ├─ models/           # SQLAlchemy ORM 模型
│  ├─ repositories/     # 数据访问层，按领域包 + 实体模块拆分
│  ├─ routers/          # FastAPI 路由
│  ├─ schemas/          # Pydantic 请求/响应模型
│  └─ services/         # 业务规则、校验、编排
├─ frontend/            # Vue 聊天前端
├─ migrations/          # Alembic 迁移
├─ data/                # SQLite 和知识库本地数据目录
├─ main.py              # FastAPI 应用入口
└─ pyproject.toml       # Python 项目配置
```

### 当前分层约定

从现有代码看，主线是：

1. `routers` 负责 HTTP 接口暴露
2. `services` 负责业务校验和流程编排
3. `repositories/<domain>/<entity>.py` 负责具体数据访问
4. `models` 和 `schemas` 分别承载 ORM 结构与 API 结构

Repository 层现在已经是这种形态：

- `app/repositories/organization/organization_unit.py`
- `app/repositories/workforce/worker.py`
- `app/repositories/workforce/worker_assignment.py`
- `app/repositories/shopfloor/production_order.py`
- `app/repositories/shopfloor/workstation.py`

同时，`app/repositories/<domain>/__init__.py` 和 `app/repositories/__init__.py` 仍然提供聚合导出，方便兼容旧调用路径。

## 领域模块与接口

后端当前挂载了 8 组业务路由和 1 组 Agent 路由。

### 组织与人员

- `/organization-units`
- `/workers`
- `/worker-assignments`

### 能力与资质

- `/skills`
- `/worker-skills`
- `/certifications`
- `/worker-certifications`
- `/safety-trainings`
- `/worker-safety-trainings`
- `/equipment-authorizations`

### 生产现场

- `/production-lines`
- `/production-teams`
- `/workstations`
- `/workstation-skill-requirements`
- `/workstation-certification-requirements`
- `/workstation-equipment-requirements`
- `/production-orders`
- `/production-operations`
- `/operational-risk-signals`
- `/operational-risk-reviews`

### 排班与出勤

- `/shift-templates`
- `/shift-plans`
- `/shift-assignments`
- `/attendance-records`
- `/leave-requests`
- `/payroll-records`

### 协同

- `/projects`
- `/project-members`
- `/project-skill-requirements`
- `/project-timesheet-entries`

### Agent

- `POST /agent/chat`
- `POST /agent/chat/stream`
- `GET /agent/sessions`
- `GET /agent/sessions/{session_id}/messages`
- `DELETE /agent/sessions/{session_id}`
- `GET /agent/skills`
- `POST /agent/skills/{skill_name}/enable`
- `POST /agent/skills/{skill_name}/disable`

## 已注册的 Agent 技能

当前 `app/agent/skills/__init__.py` 注册了以下技能：

- `core`
- `employee_skill`
- `onboarding`
- `leave`
- `attendance`
- `payroll`
- `analytics`
- `knowledge_base`
- `project`
- `memory`

这些技能由 `SkillRegistry` 管理，并在应用启动时由 `create_agent()` 完成注册。

## 前端现状

`frontend/` 当前不是完整的业务后台，而是一个面向 Agent 的聊天界面：

- 只有一个路由 `/`
- 主页面是 `frontend/src/views/ChatView.vue`
- 主要由会话侧栏、消息窗口、输入框和技能面板组成
- 支持流式消息消费

如果你在找“人员台账 / 排班列表 / 生产线配置”这类 CRUD 页面，当前代码里还没有对应的前端业务页面。

## 快速开始

### 1. 准备环境

- Python 3.13+
- Node.js
- 推荐使用 `uv`

### 2. 配置环境变量

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

然后按需填写数据库、模型服务和知识库相关配置。

当前代码实际读取的主要配置项在 `app/config.py` 中，包括：

- `DATABASE_URL`
- `DEEPSEEK_API_KEY`
- `DEEPSEEK_BASE_URL`
- `DEEPSEEK_MODEL`
- `AGENT_MAX_ITERATIONS`
- `AGENT_MAX_HISTORY_MESSAGES`
- `USE_SKILL_ROUTING`
- `DEFAULT_USER_TAG`
- `DASHSCOPE_API_KEY`
- `DASHSCOPE_BASE_URL`
- `DASHSCOPE_EMBEDDING_MODEL`
- `KNOWLEDGE_BASE_DIR`
- `KNOWLEDGE_BASE_CHUNK_SIZE`
- `KNOWLEDGE_BASE_CHUNK_OVERLAP`
- `KNOWLEDGE_BASE_SEARCH_TOP_K`

### 3. 安装后端依赖

推荐：

```bash
uv sync --dev
```

如果不用 `uv`，至少需要安装 `pyproject.toml` 里的运行依赖；开发检查还需要 `ruff`、`mypy`、`pytest`、`httpx` 等 dev 依赖。

### 4. 执行数据库迁移

```bash
alembic upgrade head
```

### 5. 启动后端

```bash
uvicorn main:app --reload
```

启动后可访问：

- API 根路径：`http://localhost:8000/`
- Swagger 文档：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`

注意：当前 CORS 允许的前端来源是 `http://localhost:5173`。

### 6. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在：

- `http://localhost:5173`

## 开发检查

当前仓库已经配置：

```bash
ruff check app/repositories app/services app/routers main.py
mypy .
```

`pyproject.toml` 中已经声明了 `pytest`、`pytest-asyncio` 和 `httpx`，但仓库当前没有独立的 `tests/` 目录，自动化测试还不是主要交付面。

## 建议阅读顺序

如果第一次接触这个仓库，建议按下面顺序看：

1. `main.py`：应用入口、CORS、路由挂载、Agent 初始化
2. `app/routers/`：系统暴露了哪些 REST 资源
3. `app/services/`：业务约束和校验逻辑
4. `app/repositories/`：领域包与实体级数据访问
5. `app/agent/`：聊天、技能注册、会话历史
6. `frontend/src/`：当前前端如何消费 Agent 接口

## 一句话总结

Workforce Ops 当前已经具备完整的制造业人力运营后端骨架，以及一个可用的 Agent 聊天前端；它的重点不在“传统 HR SaaS 页面”，而在围绕现场人员、资质、排班和生产风险，把结构化接口和可调用技能放到同一套系统里。
