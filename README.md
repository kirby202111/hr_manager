# Workforce Ops
Workforce Ops 是一个面向制造业生产现场的人力运营系统。它不是通用 HR SaaS，而是围绕产线实际协同展开，重点处理人员主数据、部门归属、技能与资质、工位资格、班次与排班、请假考勤、薪资核算，以及生产风险校验等业务。

项目由后端 API、前端控制台和一个面向业务流程的智能 Agent 组成。系统既能提供常规的增删改查接口，也支持把“新员工入职”“查询班组能力缺口”“生成月度薪资”“校验工位上岗资格”这类动作组织成可调用的技能与工作流。

## 项目目标

这个项目试图解决的不是传统人事管理的全量问题，而是制造业现场常见的几类协同难题：

- 人员信息分散，产线、班组、部门之间缺少统一主数据
- 员工技能、证书、安全培训、设备授权彼此割裂，无法快速判断是否具备上岗资格
- 排班、请假、考勤、薪资之间关联松散，后续核算容易出错
- 生产现场的岗位要求、风险信号、人员安排缺少统一视图
- 业务人员想问一个问题时，往往需要跨多个模块手动拼信息

Workforce Ops 的设计思路是：以人员与组织为基础，把技能、资质、工位、班次和风险这些生产现场对象挂在同一套业务模型上，再通过 API 与 Agent 对外提供能力。

## 核心能力

当前代码结构反映出的核心领域大致包括：

- 人员与组织
  - 人员主数据
  - 部门/组织单元
  - 员工技能与技能目录
- 现场履约
  - 考勤签到签退
  - 请假与余额计算
  - 薪资生成、发薪和工资单明细
- 生产现场
  - 产线、班组、工位
  - 工位所需技能、证书、设备授权
  - 生产画像、班组归属、班次定义、排班计划
  - 工位资格校验与风险信号
- 智能能力
  - 面向业务的技能注册
  - 入职、考勤、请假、薪资等 Agent skill
  - 会话记忆与知识库能力

## Current Architecture

- `app/models`: business-domain ORM models only
- `app/agent/models`: agent runtime ORM models only
- `app/repositories`: business repositories
- `app/agent/repositories`: agent runtime repositories
- `app/services`: business services
- `app/agent/services`: agent runtime services
- `app/routers`: business REST routers
- `app/agent/router.py`: agent REST and SSE endpoints

The agent runtime keeps its own persistence boundary for:

- long-term memories
- reminder tasks
- conversation messages

These runtime records are not exported through `app.models.__all__`.

## Repository Layout

```text
app/
  agent/
    models/
    repositories/
    schemas/
    services/
    skills/
    history.py
    react_agent.py
    router.py
    skill_registry.py
    skill_router.py
  knowledge_base/
  models/
  repositories/
  routers/
  schema.py
  schemas/
  services/
frontend/
main.py
```

## Agent Endpoints

- `POST /agent/chat`
- `POST /agent/chat/stream`
- `GET /agent/sessions`
- `GET /agent/sessions/{session_id}/messages`
- `DELETE /agent/sessions/{session_id}`
- `GET /agent/skills`
- `POST /agent/skills/{skill_name}/enable`
- `POST /agent/skills/{skill_name}/disable`

## Registered Agent Skills

The runtime currently registers these skills:

- `workforce`
- `attendance`
- `capability`
- `knowledge_base`
- `memory`

## Agent Runtime Data Model

`app/agent/models` contains:

- `AgentMemory`
- `MemoryReminder`
- `ConversationMessage`

Design constraints followed by the implementation:

- no `ForeignKey(...)` usage in agent runtime models
- explicit ORM joins for runtime relationships
- runtime models separated from business-domain models
- runtime schemas live under `app/agent/schemas`
- runtime repositories and services live under `app/agent/repositories` and `app/agent/services`

## Run Locally

### Backend

```bash
uv sync --dev
uv run python scripts/init_db.py
uvicorn main:app --reload
```

`main.py` will also auto-create any missing tables on startup, so the explicit init script is mainly useful for first-time setup or standalone database preparation.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Backend default URL:

- `http://localhost:8000`

Frontend default URL:

- `http://localhost:5173`

## Configuration

Runtime configuration is defined in `app/config.py`.

Key settings include:

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

## Validation

Useful checks:

```bash
uv run ruff check app/agent main.py --no-cache
uv run python -c "import main; print('ok')"
```
