# 当前项目 Multi-Agent 适用场景评估

## 评估结论

当前项目已经具备单 Agent + Skill Router + 业务工具调用的基础能力，覆盖员工、部门、考勤、请假、薪资、技能、项目、知识库和记忆等模块。

因此，是否引入 multi-agent 不应只看“功能多不多”，而应看任务是否具备以下特征：

- 是否跨越多个业务域，并且需要不同业务视角共同判断
- 是否存在高风险动作，例如薪资、处罚、合规、人事变更
- 是否需要先分析、再决策、再执行，而不是简单查询或写入
- 是否需要复核、解释、证据链或审计记录
- 单 Agent 是否容易因为上下文过长、工具过多而漏步骤

建议的判断门槛：

> 如果一个用户请求需要跨 3 个以上 skill，并且最终结果会触发业务决策或写入关键数据，就值得考虑 multi-agent。

## 一、不需要 Multi-Agent 的场景 / 任务

这些任务目标明确、业务边界单一、风险较低，用当前的单 Agent + tool/function calling 即可完成。引入 multi-agent 会增加编排成本、延迟和调试难度，收益不明显。

| 场景 / 任务 | 涉及模块 | 不需要 multi-agent 的原因 |
| --- | --- | --- |
| 查询员工列表、员工详情 | employee | 单一数据查询，结果不需要多角色判断 |
| 新建、修改、删除部门 | department | 标准 CRUD 操作，规则简单，业务风险较低 |
| 新建或更新员工基础信息 | employee | 如果只涉及姓名、部门、薪资等单表字段，可由单工具完成 |
| 查询某员工请假余额 | leave | 单模块查询，不涉及复杂决策 |
| 提交单条请假申请 | leave | 只要不自动审批或判断合规，单 Agent 足够 |
| 查询某月考勤记录 | attendance | 数据读取型任务，不需要多视角协作 |
| 添加考勤打卡记录 | attendance | 标准写入动作，输入明确即可 |
| 查询某员工薪资记录 | payroll | 单模块读取，风险可控 |
| 新增技能目录项 | skill_catalog | 低风险配置型操作 |
| 给员工添加技能标签 | employee_skill | 单一业务动作，当前 skill 机制已足够 |
| 查询项目列表、项目详情 | project | 信息检索型任务，单 Agent 调用项目工具即可 |
| 开关某个 skill | agent / skill_registry | 系统管理动作，不需要业务推理 |
| 普通知识库问答 | knowledge_base | 如果只是查制度或 SOP，不联动业务动作，RAG 或单 Agent 即可 |
| 保存、查询用户记忆 | agent_memory | 记忆读写本身不需要多 Agent，作为通用能力即可 |

### 小结

这类任务的共同点是：输入清楚、步骤少、单模块为主、没有明显的风险复核需求。它们适合保持轻量，用现有 skill router 分发到对应工具。

## 二、可以考虑 Multi-Agent 的场景 / 任务

这些任务已经开始跨模块，且需要一定分析或解释。但如果流程仍然可控，也可以先用单 Agent + 多工具调用实现；当结果质量、可解释性或稳定性不足时，再升级为 multi-agent。

| 场景 / 任务 | 涉及模块 | 可以考虑 multi-agent 的原因 |
| --- | --- | --- |
| 月度考勤异常分析 | attendance、employee、department | 需要识别异常并按员工、部门汇总，但通常不直接触发高风险动作 |
| 请假趋势分析 | leave、employee、department | 需要从请假类型、天数、部门维度分析趋势，适合由分析角色辅助 |
| 部门薪资分布分析 | payroll、employee、department、analytics | 涉及薪资敏感数据，分析结果可能影响管理决策，但不一定直接写入数据 |
| 员工画像摘要 | employee、attendance、leave、employee_skill、memory | 需要汇总多个维度，multi-agent 可提升结构化表达和遗漏检查 |
| 项目进度查询与摘要 | project、employee_skill、timesheet | 需要汇总项目成员、工时、技能需求和进度，但通常仍是报告型任务 |
| 技能缺口分析 | project、skill_catalog、employee_skill | 需要比对项目需求与员工技能，适合拆成需求分析和匹配分析两个角色 |
| 管理层周报 / 月报 | analytics、attendance、leave、payroll、project | 需要多模块汇总和叙事表达，可引入 Report Agent 和 Review Agent |
| 制度问答 + 轻量业务建议 | knowledge_base、leave、attendance | 需要结合制度和当前数据，但不直接执行处罚或审批时，可以先轻量处理 |
| 会话记忆驱动的个性化回复 | memory、knowledge_base、各业务模块 | 记忆可能影响回答风格和上下文选择，可考虑独立 Memory Agent 做上下文筛选 |
| 异常数据解释 | attendance、payroll、leave | 需要判断异常来自缺勤、请假、数据缺失还是规则冲突，可由多个角色交叉验证 |

### 推荐的轻量 multi-agent 方式

这类场景可以先采用“主 Agent + Reviewer/Analyst Agent”的轻量形态，而不是完整多 Agent 流程。

推荐组合：

- `Coordinator Agent`：理解用户问题，选择工具和汇总结果
- `Analyst Agent`：负责统计分析、趋势判断、异常识别
- `Review Agent`：检查结论是否有数据支撑，是否存在明显遗漏

这种方式可以控制复杂度，同时提升分析类任务的稳定性。

## 三、强烈建议 Multi-Agent 的场景 / 任务

这些任务跨多个核心模块，且会影响人事、薪资、项目资源或合规判断。它们需要不同角色互相制衡、复核和生成审计线索，适合引入 multi-agent。

| 场景 / 任务 | 涉及模块 | 强烈建议 multi-agent 的原因 |
| --- | --- | --- |
| 新员工入职全流程 | employee、department、leave、payroll、employee_skill、project、knowledge_base、memory | 涉及创建员工、初始化假期、薪资设定、技能登记、项目分配和制度说明，步骤多且容易漏项 |
| 员工转岗流程 | employee、department、project、employee_skill、payroll、knowledge_base | 需要检查部门变更、岗位技能匹配、薪资影响、项目交接和制度要求 |
| 员工离职流程 | employee、project、payroll、leave、attendance、knowledge_base | 需要处理项目移交、薪资结算、假期结余、考勤核对和离职制度，风险较高 |
| 薪资核算前复核 | payroll、attendance、leave、employee、department | 薪资属于高风险业务，必须结合考勤、请假、员工状态和薪资规则交叉校验 |
| 薪资异常名单生成 | payroll、attendance、leave、analytics | 需要判断异常原因，并区分数据错误、业务异常和真实薪资风险 |
| 考勤处罚建议 | attendance、leave、employee、knowledge_base | 涉及员工权益和制度合规，应由考勤、请假、制度、复核角色共同判断 |
| 请假审批建议 | leave、attendance、employee、department、knowledge_base | 需要考虑假期余额、历史请假、部门人力情况和制度约束 |
| 项目人员智能推荐 | project、employee_skill、employee、attendance、leave、payroll | 需要同时考虑技能匹配、可用性、请假安排、当前项目占用和人力成本 |
| 项目资源冲突检测 | project、timesheet、employee_skill、leave、attendance | 需要识别人员被多个项目占用、技能短缺、工时异常和假期冲突 |
|合规问答 + 实际操作建议 | knowledge_base、employee、leave、attendance、payroll | 既要解释制度，又要结合真实员工数据给建议，应保留证据链和复核步骤 |
| 部门人力风险诊断 | employee、attendance、leave、payroll、project、analytics | 需要综合薪资、考勤、请假、项目负载等多维信号，适合多角色分析 |
| 关键人力成本预测 | payroll、project、employee、attendance、leave | 涉及成本估算和资源规划，结论会影响管理决策，需多视角校验 |

### 推荐的 Agent 分工

针对强烈建议 multi-agent 的场景，可以采用以下角色分工：

| Agent | 职责 |
| --- | --- |
| `Coordinator Agent` | 接收用户请求，拆解任务，调度专业 Agent，汇总最终结果 |
| `Employee Agent` | 处理员工档案、部门、状态、基础信息 |
| `Attendance Agent` | 分析打卡、迟到、早退、缺勤等考勤数据 |
| `Leave Agent` | 处理请假记录、假期余额、请假趋势和审批依据 |
| `Payroll Agent` | 处理薪资记录、扣款、薪资异常和成本估算 |
| `Project Agent` | 处理项目、成员、工时、技能需求和进度 |
| `Skill Matching Agent` | 处理员工技能、项目技能需求和人员匹配 |
| `Knowledge / Policy Agent` | 从知识库检索 SOP、制度、合规依据 |
| `Memory Agent` | 提取和筛选用户偏好、上下文、历史决策记录 |
| `Review / Audit Agent` | 检查遗漏、冲突、风险点，生成可解释的复核结论 |

## 四、落地优先级建议

### 第一阶段：保持单 Agent，增强复核能力

优先做：

- 分析类任务增加 `Review Agent`
- 高风险回答增加“依据 + 风险提示 + 是否需要人工确认”
- 保留当前 Skill Router，不急于重构所有 skill

适合任务：

- 考勤异常分析
- 请假趋势分析
- 部门薪资分布分析
- 月报生成

### 第二阶段：引入 Coordinator + 专业 Agent

优先做：

- `Coordinator Agent`
- `Knowledge / Policy Agent`
- `Review / Audit Agent`
- `Employee Agent`
- `Attendance Agent`
- `Leave Agent`
- `Payroll Agent`

适合任务：

- 新员工入职全流程
- 薪资核算前复核
- 考勤处罚建议
- 请假审批建议

### 第三阶段：面向项目和组织决策扩展

优先做：

- `Project Agent`
- `Skill Matching Agent`
- `Cost / Workforce Planning Agent`

适合任务：

- 项目人员智能推荐
- 技能缺口分析
- 项目资源冲突检测
- 部门人力风险诊断

## 五、当前项目的推荐切入点

最推荐优先落地以下两个 multi-agent 场景：

### 1. 薪资核算前复核

原因：

- 涉及薪资，业务风险高
- 需要联合考勤、请假、员工状态和薪资记录
- 多 Agent 的交叉校验价值明显
- 很适合引入 `Review / Audit Agent`

建议流程：

1. `Coordinator Agent` 接收核算请求
2. `Payroll Agent` 拉取薪资记录
3. `Attendance Agent` 提供异常考勤
4. `Leave Agent` 提供请假和假期余额
5. `Employee Agent` 检查员工状态和部门
6. `Review / Audit Agent` 输出异常、依据和人工确认项

### 2. 项目人员智能推荐

原因：

- 当前项目已有 project、employee_skill、skill_catalog 等基础模块
- 推荐结果需要考虑技能、可用性、成本和项目冲突
- 单 Agent 容易只看技能匹配，忽略请假、考勤、项目占用等约束

建议流程：

1. `Coordinator Agent` 理解项目需求
2. `Project Agent` 获取项目技能需求和进度
3. `Skill Matching Agent` 匹配员工技能
4. `Leave / Attendance Agent` 检查可用性
5. `Payroll / Cost Agent` 估算人力成本
6. `Review Agent` 输出推荐名单、替代名单和风险说明

## 六、总体原则

不要为了“用了 multi-agent”而拆 Agent。当前项目中，multi-agent 的价值主要体现在：

- 复杂流程编排
- 跨模块分析
- 高风险业务复核
- 制度依据和真实数据结合
- 需要审计和解释的决策

对简单 CRUD、单模块查询、低风险配置类任务，应继续使用当前单 Agent + skill/tool 的方式，保持系统简单、快速、可维护。
