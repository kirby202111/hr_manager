# Vibe Coding Prompt — HR Manager 测试补全

## 目标

为现有 HR Manager 项目的所有后端模块编写完整的 pytest 单元测试，确保代码通过 mypy 和 ruff 检测。整个过程由 Claude Code Agent 自动执行，无需人工参与。

---

## 项目概况

这是一个 HR 管理系统，后端使用 FastAPI + SQLAlchemy 2.0 + SQLite + Pydantic v2，前端使用 Vue 3 + TypeScript。后端遵循严格的 4 层架构：

```
Router → Service → Repository → Model
```

还包含 AI Agent 系统（ReAct 模式）和 Knowledge Base（ChromaDB 向量检索）模块。

---

## 当前状态

- **代码完整度**：后端所有模块已实现（models、repositories、services、routers、schemas、agent skills、knowledge base）
- **测试覆盖**：**零测试覆盖**，无任何 pytest 测试文件
- **代码质量工具**：项目未配置 mypy 和 ruff，需安装并配置

---

## 任务分解

### Task 1: 配置测试基础设施

**目标**：安装测试和代码质量工具，建立测试运行框架。

**具体步骤**：

1. 安装开发依赖：
   ```bash
   uv pip install pytest pytest-asyncio httpx mypy ruff
   ```

2. 在 `pyproject.toml` 中添加配置：

   ```toml
   [tool.pytest.ini_options]
   testpaths = ["tests"]
   pythonpath = ["."]

   [tool.mypy]
   python_version = "3.13"
   strict = true
   warn_return_any = true
   warn_unused_configs = true
   ignore_missing_imports = true

   [tool.ruff]
   target-version = "py313"
   line-length = 120

   [tool.ruff.lint]
   select = ["E", "F", "W", "I", "N", "UP"]
   ```

3. 创建测试目录结构：
   ```
   tests/
   ├── conftest.py          # 全局 fixtures（数据库、客户端）
   ├── models/
   │   └── test_employee.py
   │   └── test_department.py
   │   └── test_attendance.py
   │   └── test_leave.py
   │   └── test_payroll.py
   │   └── test_project.py
   │   └── test_employee_skill.py
   │   └── test_skill_catalog.py
   │   └── test_agent_memory.py
   ├── repositories/
   │   └── test_employee.py
   │   └── test_department.py
   │   └── test_attendance.py
   │   └── test_leave.py
   │   └── test_payroll.py
   │   └── test_project.py
   │   └── test_employee_skill.py
   │   └── test_skill_catalog.py
   │   └── test_agent_memory.py
   ├── services/
   │   └── test_employee.py
   │   └── test_department.py
   │   └── test_attendance.py
   │   └── test_leave.py
   │   └── test_payroll.py
   │   └── test_project.py
   │   └── test_employee_skill.py
   │   └── test_skill_catalog.py
   │   └── test_agent_memory.py
   │   └── test_knowledge_base.py
   ├── routers/
   │   └── test_employee.py
   │   └── test_department.py
   │   └── test_attendance.py
   │   └── test_leave.py
   │   └── test_payroll.py
   │   └── test_project.py
   │   └── test_employee_skill.py
   │   └── test_skill_catalog.py
   │   └── test_agent_memory.py
   ├── agent/
   │   └── test_protocol.py
   │   └── test_skill_registry.py
   │   └── test_skill_router.py
   │   └── test_history.py
   │   └── test_react_agent.py
   │   └── test_skills.py
   ├── knowledge_base/
   │   └── test_chunking.py
   │   └── test_vector_store.py
   │   └── test_embeddings.py
   └── __init__.py
   ```

4. 编写 `tests/conftest.py`，提供全局 fixtures：
   - `db_session`：使用内存 SQLite（`sqlite:///:memory:`）创建隔离的数据库会话，每个测试函数使用独立数据库
   - `client`：基于 `httpx.AsyncClient` 或 `TestClient` 的 FastAPI 测试客户端
   - `sample_employee`、`sample_department` 等样本数据 fixtures

**验证标准**：
- `pytest` 可运行（即使 0 个测试也正确退出）
- `mypy app/` 不报错（或仅报告已存在的类型问题）
- `ruff check app/ tests/` 不报错

---

### Task 2: Model 层测试

**目标**：测试所有 SQLAlchemy ORM 模型的 `to_dict()` 方法和字段定义。

**覆盖的模型文件**：
- `app/models/employee.py` — Employee
- `app/models/department.py` — Department
- `app/models/attendance.py` — Attendance
- `app/models/leave.py` — Leave
- `app/models/payroll.py` — Payroll
- `app/models/project.py` — Project, ProjectSkillRequirement, ProjectMember, ProjectTimesheet
- `app/models/employee_skill.py` — EmployeeSkill
- `app/models/skill_catalog.py` — SkillCatalog
- `app/models/agent_memory.py` — AgentMemory, MemoryReminder, ConversationMessage

**测试要点**：
- 创建模型实例，验证所有字段可正确赋值
- 调用 `to_dict()`，验证返回的 dict 包含所有列且值正确
- 验证 nullable 字段可设为 None
- 验证非 nullable 字段赋值 None 时抛出 IntegrityError

**关键模式**：
```python
# 模型使用 SQLAlchemy 2.0 Mapped + mapped_column 风格
class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    department_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary: Mapped[float] = mapped_column(Float, nullable=False)
    to_dict = _to_dict  # 来自 app/models/base.py
```

---

### Task 3: Repository 层测试

**目标**：测试所有 repository 函数的数据库操作，使用真实内存 SQLite 数据库。

**覆盖的 repository 文件**：
- `app/repositories/employee.py`
- `app/repositories/department.py`
- `app/repositories/attendance.py`
- `app/repositories/leave.py`
- `app/repositories/payroll.py`
- `app/repositories/project.py`
- `app/repositories/employee_skill.py`
- `app/repositories/skill_catalog.py`
- `app/repositories/agent_memory.py`

**测试要点**：
- **CRUD 完整性**：create → get → update → delete 全流程
- **get 返回 None**：查询不存在的 ID 时返回 None
- **get_all 空列表**：无数据时返回空列表
- **update 部分更新**：只更新传入的非 None 字段
- **delete 返回 False**：删除不存在的记录时返回 False
- **过滤查询**：如 `get_employees_by_department`、按状态/日期过滤等

**关键模式**：
```python
# 每个 repository 函数自己创建 SessionLocal 会话
def get_all_employees() -> list[dict]:
    with SessionLocal() as session:
        employees = session.query(EmployeeORM).all()
        return [e.to_dict() for e in employees]
```

**注意事项**：
- Repository 直接使用 `SessionLocal()`，需要通过 monkeypatch 或 fixture 替换 `app.database.SessionLocal` 指向测试数据库
- 每个 repository 函数内部创建自己的 session，不能从外部注入
- 建议在 conftest.py 中替换 `app.database.engine` 和 `SessionLocal` 为内存数据库版本

---

### Task 4: Service 层测试

**目标**：测试所有 service 函数的业务逻辑，mock repository 层调用。

**覆盖的 service 文件**：
- `app/services/employee.py`
- `app/services/department.py`
- `app/services/attendance.py`
- `app/services/leave.py`
- `app/services/payroll.py`
- `app/services/project.py`
- `app/services/employee_skill.py`
- `app/services/skill_catalog.py`
- `app/services/agent_memory.py`
- `app/services/knowledge_base.py`

**测试要点**：
- **正常路径**：调用成功，返回正确的 Pydantic Response 对象
- **404 错误**：资源不存在时抛出 HTTPException(status_code=404)
- **400 错误**：关联资源不存在时抛出 HTTPException(status_code=400)（如 department_id 无效）
- **数据填充**：验证 `_fill_department_name`、`_fill_employee_name` 等字段填充逻辑
- **业务计算**：
  - Attendance：工时计算、迟到/早退判定（LATE_THRESHOLD=9:00, EARLY_LEAVE_THRESHOLD=18:00）
  - Leave：请假天数计算、余额扣减（年假10天、病假15天、事假5天）
  - Payroll：日薪 = salary / 21.75、扣款计算、工资单明细
  - Project：进度百分比计算、成员工作量汇总
- **Pydantic schema 构造**：验证 service 正确构造 Create/Update schema 对象传给 repo

**关键模式**：
```python
# Service 调用 repository，填充关联字段，返回 Pydantic 模型
def get_employee(employee_id: int) -> EmployeeResponse:
    employee = employee_repo.get_employee_by_id(employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    return EmployeeResponse(**_fill_department_name(employee))
```

**Mock 策略**：
```python
# 使用 unittest.mock.patch mock repository 函数
from unittest.mock import patch, MagicMock

@patch("app.services.employee.employee_repo")
def test_get_employee_not_found(mock_repo):
    mock_repo.get_employee_by_id.return_value = None
    with pytest.raises(HTTPException) as exc_info:
        employee_service.get_employee(999)
    assert exc_info.value.status_code == 404
```

---

### Task 5: Router 层测试

**目标**：测试所有 FastAPI 路由端点，使用 TestClient 进行集成测试。

**覆盖的 router 文件**：
- `app/routers/employee.py`
- `app/routers/department.py`
- `app/routers/attendance.py`
- `app/routers/leave.py`
- `app/routers/payroll.py`
- `app/routers/project.py`
- `app/routers/employee_skill.py`
- `app/routers/skill_catalog.py`
- `app/routers/agent_memory.py`

**测试要点**：
- **HTTP 方法映射**：GET/POST/PUT/DELETE 返回正确的状态码（200/201/404/400）
- **请求体验证**：缺少必填字段时返回 422
- **响应格式**：验证 JSON 结构符合 schema
- **列表端点**：验证返回 `{entities: [...], total: int}` 格式
- **特殊端点**：
  - `/attendance/check-in` (POST)、`/attendance/check-out/{id}` (PUT)
  - `/leaves/{id}/approve`、`/leaves/{id}/reject`
  - `/payroll/{id}/approve`、`/payroll/{id}/process`
  - `/leaves/employee/{id}/balance`
  - `/payroll/employee/{id}/payslip/{month}`

**关键模式**：
```python
from fastapi.testclient import TestClient

def test_list_employees(client: TestClient):
    response = client.get("/employees/")
    assert response.status_code == 200
    data = response.json()
    assert "employees" in data
    assert "total" in data

def test_create_employee(client: TestClient):
    response = client.post("/employees/", json={"name": "张三", "salary": 10000})
    assert response.status_code == 201
    assert response.json()["name"] == "张三"
```

---

### Task 6: Agent 系统测试

**目标**：测试 AI Agent 系统的核心组件。

**覆盖的文件**：
- `app/agent/protocol.py` — AgentTool、Skill、_safe()、BaseAgent、BaseHistoryStore
- `app/agent/skill_registry.py` — SkillRegistry 注册和工具解析
- `app/agent/skill_router.py` — SkillRouter 路由选择
- `app/agent/history.py` — 会话历史存储
- `app/agent/react_agent.py` — ReAct 循环（mock LLM 调用）

**测试要点**：

#### protocol.py
- `AgentTool.to_openai_tool()` 返回正确的 OpenAI function calling 格式
- `Skill.to_openai_skill_summary()` 返回正确的结构
- `Skill.get_openai_tools()` / `get_tool_map()` 在 enabled=False 时返回空
- `_safe()` 正常调用返回结果（dict / list / Pydantic 模型）
- `_safe()` 捕获 HTTPException 返回 `{"error": detail}`
- `_safe()` 捕获普通 Exception 返回 `{"error": str(e)}`

#### skill_registry.py
- 注册 skill 后能通过工具名查找
- 列出所有 skills
- 获取所有工具的 OpenAI 格式

#### skill_router.py
- mock LLM 响应，验证 skill 选择逻辑
- 无匹配 skill 时的行为

#### history.py
- 添加/获取/清空会话消息
- 列出所有会话

#### react_agent.py
- mock LLM 和 skill_registry，验证 chat 循环的完整流程
- 验证 max_iterations 限制
- 验证 memory 注入

**Mock 策略**：
- Agent 模块依赖 DeepSeek API，所有 LLM 调用必须 mock
- 使用 `unittest.mock.patch("app.agent.react_agent.OpenAI")` mock OpenAI client
- SkillRouter 中的 LLM 调用也需要 mock

---

### Task 7: Agent Skills 测试

**目标**：测试所有 agent skill 的工具定义和调用逻辑。

**覆盖的 skill 文件**：
- `app/agent/skills/core.py` — employee_management
- `app/agent/skills/employee_skill.py` — skill_management
- `app/agent/skills/onboarding.py` — onboarding
- `app/agent/skills/leave.py` — leave_management
- `app/agent/skills/attendance.py` — attendance_management
- `app/agent/skills/payroll.py` — payroll_processing
- `app/agent/skills/analytics.py` — analytics
- `app/agent/skills/knowledge_base.py` — knowledge_base
- `app/agent/skills/project.py` — project_management
- `app/agent/skills/memory.py` — memory

**测试要点**：
- 每个 Skill 对象的 `name`、`description`、`applicability` 正确
- 每个 Skill 的 `tools` 列表长度与预期一致
- 每个 AgentTool 的 `name`、`description`、`parameters` 格式正确
- 调用 AgentTool.fn()，mock service 层，验证正确调用 service 函数
- 验证 `_safe()` 包装：service 抛出 HTTPException 时返回 `{"error": ...}`
- 验证 Create/Update 工具正确构造 Pydantic schema 对象

**关键模式**：
```python
# Skill 工具通过 _safe() 包装 service 调用
AgentTool(
    name="create_employee",
    description="创建新员工",
    parameters={"type": "object", "properties": {...}, "required": [...]},
    fn=lambda name, salary, department_id=None: _safe(
        employee_service.create_employee,
        EmployeeCreate(name=name, department_id=department_id, salary=salary),
    ),
)
```

---

### Task 8: Knowledge Base 测试

**目标**：测试知识库的文档处理和向量检索功能。

**覆盖的文件**：
- `app/knowledge_base/chunking.py` — 文本分块
- `app/knowledge_base/embeddings.py` — 向量嵌入
- `app/knowledge_base/vector_store.py` — ChromaDB 操作
- `app/services/knowledge_base.py` — 知识库业务逻辑

**测试要点**：

#### chunking.py
- 短文本（< chunk_size）返回单个块
- 长文本按 chunk_size 切分
- 块之间有 overlap 重叠
- 优先在换行符处切分
- 空文本返回空列表

#### embeddings.py
- mock DashScope API，验证调用参数
- 批量嵌入的分批逻辑（EMBED_BATCH_SIZE=20）
- API 错误时的异常处理

#### vector_store.py
- mock ChromaDB，验证 add/search/delete/list 操作
- 验证 cosine similarity 分数映射到 0-1 范围
- 验证批量添加文档的流程

#### knowledge_base service
- mock vector_store，验证搜索、添加、删除、列表操作
- 验证文档添加时的分块和嵌入流程

---

### Task 9: 代码质量检查与修复

**目标**：确保所有代码（包括新写的测试代码）通过 mypy 和 ruff 检查。

**具体步骤**：

1. 运行 `ruff check app/ tests/ --fix` 自动修复格式问题
2. 运行 `ruff format app/ tests/` 格式化代码
3. 运行 `mypy app/ tests/` 检查类型，修复所有错误
4. 如果现有 app 代码有 mypy 错误，在 `pyproject.toml` 中按模块添加 `[[tool.mypy.overrides]]` 忽略（不修改业务代码）
5. 确保测试代码完全通过 mypy strict 检查

---

## 执行策略

### 主 Agent 编排

主 Agent 按以下顺序调度子 Agent，每个子 Agent 完成后验证结果再启动下一个：

```
Task 1（基础设施）→ Task 2（Model）→ Task 3（Repository）→ Task 4（Service）
→ Task 5（Router）→ Task 6（Agent）→ Task 7（Skills）→ Task 8（KB）→ Task 9（质量）
```

### 子 Agent 执行规范

每个子 Agent 必须：

1. **先读后写**：读取要测试的源文件，理解实现细节
2. **编写测试**：按上述测试要点编写完整的 pytest 测试
3. **本地验证**：运行 `pytest tests/<对应目录>/ -v` 确保全部通过
4. **质量检查**：运行 `ruff check` 和 `mypy` 确保无错误
5. **报告结果**：返回测试数量、通过数量、覆盖率摘要

### 并行执行

以下 Task 之间无依赖，可并行执行：
- Task 2 + Task 6 + Task 7 + Task 8（Model/Agent/Skills/KB 互不依赖）
- 但 Task 3 依赖 Task 2 的 conftest 数据库 fixture
- Task 4 依赖 Task 3（mock 需要理解 repo 接口）
- Task 5 依赖 Task 4（需要理解 service 行为）

推荐执行顺序（3 轮并行）：

**第 1 轮**：Task 1（基础设施，必须先完成）
**第 2 轮**：Task 2 + Task 6 + Task 7 + Task 8（并行）
**第 3 轮**：Task 3 + Task 4 + Task 5（顺序执行，因有依赖）
**第 4 轮**：Task 9（质量检查，最后执行）

---

## 关键约束

1. **不修改业务代码**：只添加测试代码和配置，不修改 `app/` 下的任何业务逻辑代码
2. **使用内存 SQLite**：测试数据库使用 `sqlite:///:memory:`，不触碰 `data/hr_system.db`
3. **Mock 外部依赖**：DeepSeek API、DashScope API、ChromaDB 均需 mock，不发起真实 API 调用
4. **中文响应**：错误消息中的中文文本需在测试中断言
5. **独立测试**：每个测试函数独立，不依赖其他测试的执行顺序
6. **类型安全**：所有测试代码通过 mypy strict 检查
7. **代码风格**：所有代码通过 ruff 检查和格式化

---

## 验收标准

- [ ] `pytest tests/ -v` 全部通过，0 failures
- [ ] `mypy app/ tests/ --strict` 无错误（或有明确 override 的已知问题）
- [ ] `ruff check app/ tests/` 无错误
- [ ] `ruff format --check app/ tests/` 格式正确
- [ ] 测试覆盖所有 9 个 Model、9 个 Repository、10 个 Service、9 个 Router、5 个 Agent 组件、10 个 Skill、4 个 Knowledge Base 模块
- [ ] 每个 CRUD 模块至少覆盖：创建成功、查询成功、查询不存在、更新成功、删除成功、删除不存在
- [ ] Service 层测试覆盖所有 HTTPException 路径（404、400）
- [ ] Router 层测试覆盖所有 HTTP 方法（GET/POST/PUT/DELETE）和状态码
- [ ] Agent `_safe()` 函数的 3 条路径（正常、HTTPException、Exception）全部测试
