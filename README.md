# Workforce Ops

Workforce Ops 是一个面向制造业现场的人力运营与智能问答项目。当前代码库包含两条主线能力：

- 一套围绕制造现场人员、组织、资质、排班、考勤和风险的业务后端 API
- 一个带会话、流式回复、技能开关和知识库检索能力的 Agent 控制台

它不是通用 HR SaaS，而是把制造现场常见的人、岗、线、班、工位、订单和风险对象放在同一套业务模型下，便于做人员信息维护、现场归属管理、资质记录、排班落位、考勤留痕，以及基于知识库和技能路由的业务问答。

## 项目目标

当前项目主要解决以下几类问题：

- 用统一的数据模型管理组织、员工、产线、班组、工位和生产订单
- 沉淀员工技能、证书、安全培训、设备授权等上岗相关信息
- 支持班次模板、排班计划和人员排班分配的结构化维护
- 记录考勤、请假、薪资和现场运营风险信号
- 通过 Agent 将业务查询、知识库检索和历史记忆组合成可交互的问答能力

## 核心能力

当前代码结构反映出的核心能力包括：

- 业务主数据
  - 组织单元管理
  - 员工主档与任职分配管理
  - 技能目录与员工技能管理
  - 证书、安全培训、员工培训记录和设备授权管理
- 制造现场建模
  - 产线、班组、工位管理
  - 生产订单与生产工序管理
  - 班次模板、排班计划、排班分配管理
- 现场运营记录
  - 考勤记录
  - 请假申请
  - 薪资记录
  - 运营风险信号与风险复核
- Agent 能力
  - `POST /agent/chat` 与 `POST /agent/chat/stream` 对话接口
  - 技能注册、启停和技能路由
  - 会话消息持久化与记忆能力
  - 基于 ChromaDB 的本地知识库检索
- 前端控制台
  - 单页聊天界面
  - 会话侧边栏
  - 流式消息展示
  - 技能面板与技能开关

## Current Architecture

- `app/models`: 业务域 ORM 模型
- `app/agent/models`: Agent 运行时 ORM 模型
- `app/repositories`: 业务仓储层
- `app/agent/repositories`: Agent 运行时仓储层
- `app/services`: 业务服务层
- `app/agent/services`: Agent 运行时服务层
- `app/routers`: 业务 REST 路由
- `app/agent/router.py`: Agent REST 与 SSE 路由
- `app/knowledge_base`: 文档切分、向量化与检索能力
- `frontend/src`: Vue 3 聊天控制台

业务后端当前按九个领域拆分：

- `organization`
- `workforce`
- `capability`
- `qualification`
- `shopfloor`
- `production`
- `staffing`
- `attendance`
- `risk`

Agent 运行时与业务域持久化边界分离，运行时数据不通过 `app.models.__all__` 暴露。

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

当前默认注册的技能为：

- `workforce`
- `attendance`
- `capability`
- `knowledge_base`
- `memory`

## Agent Runtime Data Model

`app/agent/models` 当前包含：

- `AgentMemory`
- `MemoryReminder`
- `ConversationMessage`

实现中遵循的约束包括：

- 运行时模型不使用 `ForeignKey(...)`
- 运行时关系通过显式 ORM 查询维护
- 运行时模型与业务域模型分离
- 运行时 schema 位于 `app/agent/schemas`
- 运行时仓储与服务位于 `app/agent/repositories` 和 `app/agent/services`

## Run Locally

### Backend

```bash
uv sync --dev
uv run python scripts/init_db.py
uvicorn main:app --reload
```

`main.py` 启动时会自动初始化缺失表结构，因此初始化脚本主要用于首次建库或单独准备数据库。

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

运行配置定义在 `app/config.py`，主要包括：

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

常用检查命令：

```bash
uv run ruff check app main.py --no-cache
uv run python -c "import main; print('ok')"
```
