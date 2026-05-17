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

Workforce Ops 的设计思路是：以人员与组织为基础，把技能、资质、工位、班次、项目和风险这些生产现场对象挂在同一套业务模型上，再通过 API 与 Agent 对外提供能力。

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
- 项目协同
  - 项目、成员、技能需求、工时报工
- 智能能力
  - 面向业务的技能注册
  - 入职、考勤、请假、薪资、项目等 Agent skill
  - 会话记忆与知识库能力

## 技术栈

### 后端

- Python 3.13
- FastAPI
- SQLAlchemy 2
- Alembic
- Pydantic
- SSE Starlette
- ChromaDB

### 前端

- Vue 3
- Vite
- TypeScript
- Element Plus
- Pinia

### 智能 Agent

- OpenAI SDK 兼容调用
- 可配置的推理模型与 Embedding 模型
- 业务技能路由、工作流封装、会话记忆

## 目录结构

```text
.
├─ app
│  ├─ agent            # Agent、技能、记忆、知识库相关逻辑
│  ├─ models           # ORM 模型
│  ├─ repositories     # 数据访问层
│  ├─ routers          # FastAPI 路由
│  ├─ schemas          # 请求/响应模型
│  └─ services         # 业务服务层
├─ frontend            # Vue 前端
├─ migrations          # Alembic 迁移
├─ data                # 本地数据库与知识库数据
└─ main.py             # FastAPI 应用入口
```

## 后端接口概览

从入口文件和路由组织来看，当前后端已经覆盖这些主要接口域：

- `worker`
- `org_unit`
- `attendance`
- `leave`
- `payroll`
- `worker_skill`
- `skill_definition`
- `project`
- `shopfloor`
- `agent_memory`
- `agent`

另外，仓库里还能看到 `credential`、`safety_compliance`、`shift_staffing`、`shopfloor_structure`、`shopfloor_worker_profile`、`operational_risk`、`work_order` 等更细分的领域模块，它们共同构成生产现场运营能力。

## 快速开始

### 1. 准备环境

- 安装 Python 3.13
- 安装 Node.js
- 准备可用的虚拟环境工具或直接使用项目内 `.venv`

### 2. 配置后端环境变量

复制 `.env.example` 为 `.env`，并根据实际环境填写：

```env
DATABASE_URL=sqlite:///./data/hr_system.db

DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash

AGENT_MAX_ITERATIONS=10
AGENT_MAX_HISTORY_MESSAGES=50
USE_SKILL_ROUTING=true

DASHSCOPE_API_KEY=your_dashscope_api_key_here
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
DASHSCOPE_EMBEDDING_MODEL=text-embedding-v4

KNOWLEDGE_BASE_DIR=./data/knowledge_base
KNOWLEDGE_BASE_CHUNK_SIZE=500
KNOWLEDGE_BASE_CHUNK_OVERLAP=100
```

### 3. 安装后端依赖

如果你使用 `uv`：

```bash
uv sync
```

如果你使用 `pip`，需要按 `pyproject.toml` 中的依赖自行安装。

### 4. 执行数据库迁移

```bash
alembic upgrade head
```

### 5. 启动后端

```bash
uvicorn main:app --reload
```

默认情况下，后端会开放给前端本地开发地址 `http://localhost:5173`。

### 6. 启动前端

```bash
cd frontend
npm install
npm run dev
```

## 测试与开发

### 类型检查

```bash
mypy .
```

### 代码风格检查

```bash
ruff check .
```

## Agent 能力说明

这个项目的一个明显特点，是它不只是一组 REST API。`app/agent` 下还定义了面向业务动作的技能层，典型能力包括：

- 人员管理
- 入职流程
- 考勤查询与签到
- 请假申请与余额查询
- 薪资生成与查询
- 项目成员与工时查询
- 知识库检索
- 会话记忆

这意味着系统未来可以同时支持两种使用方式：

- 前端表单和常规 API 调用
- 面向自然语言任务的业务 Agent 调度

## 适用场景

这个项目尤其适合下面这类场景：

- 制造业工厂的现场人力运营平台
- 需要把技能、证书、安全培训和岗位资格联动起来的系统
- 需要让排班、请假、考勤、薪资共享同一套人员数据的系统
- 希望在业务后台中引入流程型 Agent 的内部工具

## 当前状态

从代码组织来看，项目已经具备比较完整的领域拆分和模块边界，但仍处在持续演进阶段。部分模块命名与领域重构仍在推进中，阅读和二次开发时应优先以 `models / schemas / services / routers` 这一套纵向分层为主线理解系统。

## 建议的阅读顺序

如果你第一次接触这个仓库，比较顺手的阅读路径是：

1. `main.py`：看应用入口和路由装配
2. `app/routers`：看系统提供了哪些接口域
3. `app/services`：看核心业务规则
4. `app/models`：看数据对象之间的关系
5. `app/agent/skills`：看 Agent 能力如何映射到业务动作
6. `frontend/src`：看前端如何消费这些能力

## 一句话总结

Workforce Ops 更像一个“制造业现场人力运营中台”，而不是简单的员工信息系统。它把人、技能、工位、班次、请假、薪资和风险校验放进了同一个业务上下文里，并为后续接入 Agent 工作流留出了明确接口。
