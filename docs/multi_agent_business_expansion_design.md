# Multi-Agent 业务扩展详细设计：工厂生产制造人员管理

## 1. 背景

当前项目已经具备员工、部门、考勤、请假、薪资、技能、项目、知识库、Agent 记忆和 Skill Router 等基础能力。

但从业务定位看，本项目更适合聚焦在工厂生产制造场景下的人员管理，而不是泛 HR 管理。也就是说，系统的核心对象不应只是“员工”，还应进一步围绕生产现场中的班组、产线、工位、技能资质、安全培训、排班、工时、质量记录和设备授权展开。

在这个定位下，multi-agent 的价值主要体现在：

- 生产排班需要同时考虑产能、技能、考勤、请假和合规
- 关键工位需要资质、培训、安全规则和设备授权共同校验
- 生产异常需要追溯人员、班次、工位、设备和质量记录
- 班组长、生产主管、HR、EHS、安全、质量和财务关注点不同
- 高风险操作需要复核和审计，例如安排未认证人员上岗、特殊工种加班、设备操作授权

本文档基于“工厂生产制造人员管理”的边界，重新设计用于支撑 multi-agent 的业务扩展方案。

## 2. 业务边界

### 2.1 项目聚焦

本项目聚焦以下人员管理范围：

- 一线生产员工管理
- 班组和产线人员管理
- 工位和岗位资质管理
- 生产排班与调班
- 考勤、请假、加班和工时
- 安全培训和上岗认证
- 设备操作授权
- 质量异常中的人员因素追溯
- 生产人力成本和产能分析
- 现场风险预警


## 3. 设计目标

### 3.1 业务目标

- 支持工厂现场的排班、调班、加班、上岗资质和安全合规
- 帮助班组长和生产主管快速判断人员是否适合某个工位或班次
- 对高风险人员安排进行复核和预警
- 将知识库中的 SOP、安全规则、质量要求用于实际人员决策
- 支持生产异常和质量异常中的人员维度追溯
- 为生产人力成本、产能和技能缺口提供分析依据

### 3.2 技术目标

- 保留当前单 Agent + Skill Router 架构
- 在复杂制造场景中引入 Coordinator Agent 和专业 Agent
- 优先复用现有 employee、attendance、leave、payroll、employee_skill、project、knowledge_base 模块
- 新增制造现场人员管理相关模块
- 所有高风险建议保留人工确认和审计记录

## 4. 总体扩展方向

建议围绕以下制造人员管理能力扩展：

1. 班组、产线与工位管理
2. 生产排班与调班
3. 岗位资质、技能认证与设备授权
4. 安全培训与 EHS 合规
5. 加班、工时与计件/工序薪酬
6. 生产异常与质量追溯
7. 产能、人力缺口与技能缺口分析
8. 现场风险预警与审批复核

优先级最高的是：

1. 班组、产线与工位管理
2. 生产排班与调班
3. 岗位资质、技能认证与设备授权
4. 安全培训与 EHS 合规
5. 现场风险预警与审批复核

## 5. 推荐 Multi-Agent 架构

### 5.1 当前架构

```text
User
  -> ReActAgent
    -> SkillRouter
      -> Business Skills
        -> Services
          -> Repositories
            -> Database
```

该结构适合单意图、单模块、低风险任务。

### 5.2 制造场景扩展架构

```text
User
  -> Coordinator Agent
    -> Production Staffing Agent
    -> Shift Scheduling Agent
    -> Skill & Certification Agent
    -> Attendance & Leave Agent
    -> Safety / EHS Agent
    -> Quality Trace Agent
    -> Payroll / Labor Cost Agent
    -> Knowledge / SOP Agent
    -> Risk & Audit Agent
  -> Recommendation / Approval / Action Plan
```

### 5.3 Agent 分工

| Agent | 职责 |
| --- | --- |
| Coordinator Agent | 理解请求，拆解任务，调度专业 Agent，汇总最终建议 |
| Production Staffing Agent | 处理班组、产线、工位、人力需求和人员调配 |
| Shift Scheduling Agent | 处理排班、调班、倒班、加班和班次冲突 |
| Skill & Certification Agent | 校验技能等级、岗位资质、特殊工种认证和设备授权 |
| Attendance & Leave Agent | 分析考勤、请假、缺勤、迟到和出勤可用性 |
| Safety / EHS Agent | 检查安全培训、上岗规则、禁忌安排和 EHS 风险 |
| Quality Trace Agent | 追溯质量异常涉及的人员、班次、工位和操作记录 |
| Payroll / Labor Cost Agent | 估算加班、计件、班次津贴和人力成本 |
| Knowledge / SOP Agent | 检索 SOP、安全制度、质量标准和岗位作业指导书 |
| Risk & Audit Agent | 复核高风险安排，输出风险、依据和人工确认项 |

## 6. 模块一：班组、产线与工位管理

### 6.1 业务价值

工厂人员管理的核心不是抽象部门，而是具体到班组、产线和工位。只有建立这些现场对象，Agent 才能判断“谁能上哪条线、哪个工位、哪个班次”。

### 6.2 核心能力

- 班组管理
- 产线管理
- 工位管理
- 工位所需技能和资质
- 工位风险等级
- 班组长和产线负责人
- 员工默认班组和可支援产线

### 6.3 建议数据模型

#### production_lines

| 字段 | 说明 |
| --- | --- |
| id | 产线 ID |
| name | 产线名称 |
| department_id | 所属部门 |
| supervisor_employee_id | 产线负责人 |
| status | active、paused、inactive |
| description | 描述 |

#### production_teams

| 字段 | 说明 |
| --- | --- |
| id | 班组 ID |
| name | 班组名称 |
| line_id | 默认产线 |
| leader_employee_id | 班组长 |
| shift_type | day、night、rotating |
| status | active、inactive |

#### workstations

| 字段 | 说明 |
| --- | --- |
| id | 工位 ID |
| line_id | 所属产线 |
| code | 工位编码 |
| name | 工位名称 |
| risk_level | low、medium、high |
| required_skill_ids | 所需技能 JSON |
| required_certification_ids | 所需资质 JSON |
| equipment_ids | 涉及设备 JSON |

#### employee_team_assignments

| 字段 | 说明 |
| --- | --- |
| id | 记录 ID |
| employee_id | 员工 ID |
| team_id | 班组 ID |
| line_id | 产线 ID |
| start_date | 开始日期 |
| end_date | 结束日期 |
| is_primary | 是否主班组 |

### 6.4 Multi-Agent 场景

用户请求：

> 明天 A 线缺 2 个人，帮我从 B 班组找可支援人员。

建议流程：

1. Production Staffing Agent 查询 A 线工位缺口
2. Skill & Certification Agent 校验候选人员技能和资质
3. Attendance & Leave Agent 检查明天是否请假或缺勤风险
4. Safety / EHS Agent 检查是否有高风险工位限制
5. Risk & Audit Agent 复核是否存在违规安排
6. Coordinator Agent 输出推荐人员和替代方案

## 7. 模块二：生产排班与调班

### 7.1 业务价值

排班是制造现场最适合 multi-agent 的场景之一。它天然跨越人力需求、考勤、请假、技能、工位、安全和成本。

### 7.2 核心能力

- 班次定义
- 产线排班
- 员工排班
- 调班申请
- 加班申请
- 缺勤补位
- 连续夜班和超时预警
- 人工确认和审批记录

### 7.3 建议数据模型

#### shift_definitions

| 字段 | 说明 |
| --- | --- |
| id | 班次 ID |
| code | 班次编码 |
| name | 班次名称 |
| start_time | 开始时间 |
| end_time | 结束时间 |
| shift_type | day、night、overtime |
| allowance_rate | 班次津贴系数 |

#### production_shift_plans

| 字段 | 说明 |
| --- | --- |
| id | 排班计划 ID |
| line_id | 产线 ID |
| shift_id | 班次 ID |
| work_date | 日期 |
| required_headcount | 所需人数 |
| status | draft、published、adjusted、closed |

#### employee_shift_assignments

| 字段 | 说明 |
| --- | --- |
| id | 员工排班 ID |
| plan_id | 排班计划 ID |
| employee_id | 员工 ID |
| workstation_id | 工位 ID |
| assignment_type | normal、support、overtime、replacement |
| status | planned、confirmed、cancelled |

#### shift_change_requests

| 字段 | 说明 |
| --- | --- |
| id | 调班申请 ID |
| employee_id | 员工 ID |
| original_assignment_id | 原排班 |
| target_assignment_id | 目标排班 |
| reason | 调班原因 |
| status | pending、approved、rejected |
| risk_level | low、medium、high |

### 7.4 Multi-Agent 场景：缺勤补位

用户请求：

> 夜班有 1 名焊接工请假，帮我找一个合规替补。

涉及 Agent：

- Shift Scheduling Agent
- Skill & Certification Agent
- Attendance & Leave Agent
- Safety / EHS Agent
- Payroll / Labor Cost Agent
- Risk & Audit Agent

输出：

- 首选替补人员
- 备选人员
- 资质和技能依据
- 是否会产生加班或夜班津贴
- 是否违反连续工作时长限制
- 是否需要班组长确认

## 8. 模块三：岗位资质、技能认证与设备授权

### 8.1 业务价值

制造现场中，“会不会做”和“能不能合法合规上岗”是两件事。系统需要区分技能、资质和授权。

### 8.2 核心能力

- 员工技能等级
- 岗位资质认证
- 特殊工种证书
- 设备操作授权
- 认证有效期
- 到期提醒
- 上岗前自动校验

### 8.3 建议数据模型

#### certifications

| 字段 | 说明 |
| --- | --- |
| id | 资质 ID |
| name | 资质名称 |
| category | safety、equipment、process、quality |
| required_training_hours | 所需培训学时 |
| validity_months | 有效期月数 |
| description | 描述 |

#### employee_certifications

| 字段 | 说明 |
| --- | --- |
| id | 员工资质 ID |
| employee_id | 员工 ID |
| certification_id | 资质 ID |
| issued_at | 发证日期 |
| expires_at | 到期日期 |
| status | valid、expired、revoked |
| evidence | 证明材料 |

#### equipment_authorizations

| 字段 | 说明 |
| --- | --- |
| id | 授权 ID |
| employee_id | 员工 ID |
| equipment_code | 设备编码 |
| authorization_level | observer、operator、maintainer |
| issued_at | 授权日期 |
| expires_at | 到期日期 |
| status | valid、expired、revoked |

### 8.4 Multi-Agent 场景：高风险工位上岗校验

用户请求：

> 把李四安排到 A 线激光切割工位，检查是否可以上岗。

涉及 Agent：

- Production Staffing Agent
- Skill & Certification Agent
- Safety / EHS Agent
- Knowledge / SOP Agent
- Risk & Audit Agent

输出：

- 是否可以上岗
- 缺失技能或资质
- 设备授权状态
- 安全培训是否有效
- SOP 或制度依据
- 是否必须人工复核

## 9. 模块四：安全培训与 EHS 合规

### 9.1 业务价值

工厂人员管理必须把安全培训和 EHS 合规作为核心能力。Agent 的建议如果忽略安全规则，会带来很高风险。

### 9.2 核心能力

- 安全课程
- 岗前培训
- 年度复训
- 特殊工种培训
- 培训考试
- 安全违规记录
- 高风险工位限制
- EHS 规则知识库

### 9.3 建议数据模型

#### safety_trainings

| 字段 | 说明 |
| --- | --- |
| id | 培训 ID |
| title | 培训名称 |
| category | general、line、equipment、hazard |
| required_for_certification_id | 关联资质 |
| validity_months | 有效期 |
| description | 描述 |

#### employee_safety_records

| 字段 | 说明 |
| --- | --- |
| id | 记录 ID |
| employee_id | 员工 ID |
| training_id | 培训 ID |
| completed_at | 完成时间 |
| score | 考试成绩 |
| expires_at | 到期日期 |
| status | valid、expired、failed |

#### safety_incidents

| 字段 | 说明 |
| --- | --- |
| id | 安全事件 ID |
| employee_id | 相关员工 |
| line_id | 产线 |
| workstation_id | 工位 |
| incident_date | 发生日期 |
| severity | low、medium、high、critical |
| summary | 摘要 |
| status | open、reviewed、closed |

### 9.4 Multi-Agent 场景：高风险排班复核

用户请求：

> 检查下周夜班排班里是否有人不符合安全上岗要求。

涉及 Agent：

- Shift Scheduling Agent
- Skill & Certification Agent
- Safety / EHS Agent
- Knowledge / SOP Agent
- Risk & Audit Agent

输出：

- 不合规人员列表
- 不合规原因
- 涉及工位和班次
- 制度依据
- 替换建议
- 风险等级

## 10. 模块五：加班、工时与计件/工序薪酬

### 10.1 业务价值

制造场景中的薪资往往与班次、加班、工时、计件、工序补贴相关。薪资模块需要从单纯工资记录扩展为生产工时和制造薪酬核算。

### 10.2 核心能力

- 加班申请和审批
- 工时记录
- 产线工时汇总
- 工序补贴
- 夜班津贴
- 计件记录
- 薪资前置校验

### 10.3 建议数据模型

#### overtime_requests

| 字段 | 说明 |
| --- | --- |
| id | 加班申请 ID |
| employee_id | 员工 ID |
| line_id | 产线 |
| work_date | 日期 |
| hours | 加班小时 |
| reason | 原因 |
| status | pending、approved、rejected |
| risk_level | low、medium、high |

#### production_work_logs

| 字段 | 说明 |
| --- | --- |
| id | 工时记录 ID |
| employee_id | 员工 ID |
| line_id | 产线 |
| workstation_id | 工位 |
| work_date | 日期 |
| shift_id | 班次 |
| hours | 工时 |
| output_quantity | 产量 |
| defect_quantity | 不良数 |

#### piecework_records

| 字段 | 说明 |
| --- | --- |
| id | 计件记录 ID |
| employee_id | 员工 ID |
| process_code | 工序编码 |
| quantity | 数量 |
| unit_rate | 单价 |
| work_date | 日期 |
| source_log_id | 来源工时记录 |

### 10.4 Multi-Agent 场景：薪资核算前复核

用户请求：

> 核对本月夜班、加班和计件记录，找出薪资核算风险。

涉及 Agent：

- Payroll / Labor Cost Agent
- Attendance & Leave Agent
- Shift Scheduling Agent
- Production Staffing Agent
- Risk & Audit Agent

输出：

- 加班异常
- 工时与考勤不一致
- 计件产量异常
- 夜班津贴异常
- 需要人工确认的记录
- 薪资核算风险等级

## 11. 模块六：生产异常与质量追溯

### 11.1 业务价值

质量异常往往需要追溯到班次、工位、人员、设备、SOP 和培训记录。这个场景天然需要多个 Agent 协作。

### 11.2 核心能力

- 质量异常记录
- 异常关联产线、工位、班次、员工
- 关联 SOP 和质量标准
- 关联培训和资质记录
- 生成人员因素分析
- 生成整改建议

### 11.3 建议数据模型

#### quality_incidents

| 字段 | 说明 |
| --- | --- |
| id | 质量异常 ID |
| line_id | 产线 |
| workstation_id | 工位 |
| shift_id | 班次 |
| incident_date | 日期 |
| defect_type | 缺陷类型 |
| defect_quantity | 缺陷数量 |
| severity | low、medium、high、critical |
| summary | 摘要 |
| status | open、reviewed、closed |

#### quality_incident_employees

| 字段 | 说明 |
| --- | --- |
| id | 关联 ID |
| incident_id | 质量异常 ID |
| employee_id | 员工 ID |
| role | operator、inspector、team_leader |
| note | 说明 |

#### corrective_actions

| 字段 | 说明 |
| --- | --- |
| id | 整改动作 ID |
| incident_id | 质量异常 ID |
| owner_employee_id | 负责人 |
| action | 整改动作 |
| due_date | 截止日期 |
| status | open、done、cancelled |

### 11.4 Multi-Agent 场景：质量异常人员因素分析

用户请求：

> 分析昨天 A 线焊接不良率升高是否与人员安排有关。

涉及 Agent：

- Quality Trace Agent
- Production Staffing Agent
- Skill & Certification Agent
- Shift Scheduling Agent
- Knowledge / SOP Agent
- Risk & Audit Agent

输出：

- 涉及班次、工位和人员
- 是否存在新手上岗、资质过期、跨线支援
- 是否存在连续加班或夜班疲劳风险
- 相关 SOP 或质量标准
- 人员因素结论
- 建议整改动作

## 12. 模块七：产能、人力缺口与技能缺口分析

### 12.1 业务价值

制造现场经常需要回答：某条线今天能不能开满？缺什么人？缺什么技能？是否需要跨线支援？这类问题非常适合 multi-agent。

### 12.2 核心能力

- 产线人力需求
- 工位人力需求
- 班次人力缺口
- 技能缺口
- 资质缺口
- 跨线支援建议
- 培训补足建议

### 12.3 建议数据模型

#### staffing_requirements

| 字段 | 说明 |
| --- | --- |
| id | 需求 ID |
| line_id | 产线 |
| workstation_id | 工位 |
| shift_id | 班次 |
| work_date | 日期 |
| required_headcount | 所需人数 |
| required_skill_ids | 技能要求 JSON |
| required_certification_ids | 资质要求 JSON |

#### staffing_gap_analyses

| 字段 | 说明 |
| --- | --- |
| id | 缺口分析 ID |
| line_id | 产线 |
| work_date | 日期 |
| shift_id | 班次 |
| gap_summary | 缺口摘要 |
| suggestions | 建议 JSON |
| created_by | human 或 agent |
| created_at | 创建时间 |

### 12.4 Multi-Agent 场景：次日生产人力检查

用户请求：

> 检查明天所有产线排班，看看哪里有人力或资质缺口。

涉及 Agent：

- Production Staffing Agent
- Shift Scheduling Agent
- Skill & Certification Agent
- Attendance & Leave Agent
- Safety / EHS Agent
- Risk & Audit Agent

输出：

- 缺口产线
- 缺口工位
- 缺口人数
- 缺失技能或资质
- 可支援人员
- 风险等级
- 建议处理动作

## 13. 模块八：现场风险预警与审批复核

### 13.1 业务价值

制造人员管理中很多风险不来自单条数据，而来自多个弱信号组合，例如连续夜班、资质临期、近期质量异常、请假导致替补不足。风险预警模块能让 multi-agent 成为生产管理的决策支持能力。

### 13.2 风险类型

- 未认证人员上岗风险
- 资质或培训过期风险
- 连续夜班和疲劳风险
- 加班超时风险
- 高风险工位缺人风险
- 跨线支援质量风险
- 关键工位无人备份风险
- 工时与考勤不一致风险
- 质量异常人员因素风险

### 13.3 建议数据模型

#### production_risk_signals

| 字段 | 说明 |
| --- | --- |
| id | 风险信号 ID |
| employee_id | 员工 ID，可为空 |
| line_id | 产线 ID，可为空 |
| workstation_id | 工位 ID，可为空 |
| shift_assignment_id | 排班 ID，可为空 |
| signal_type | 风险类型 |
| severity | low、medium、high、critical |
| evidence | 证据 JSON |
| status | open、reviewed、resolved、ignored |
| detected_by | human 或 agent |
| created_at | 创建时间 |

#### production_risk_reviews

| 字段 | 说明 |
| --- | --- |
| id | 风险复核 ID |
| risk_signal_id | 风险信号 ID |
| reviewer | 复核人或 Agent |
| conclusion | 复核结论 |
| action_suggestion | 处理建议 |
| created_at | 创建时间 |

### 13.4 Multi-Agent 场景：排班发布前复核

用户请求：

> 发布明天排班前，帮我检查高风险安排。

涉及 Agent：

- Shift Scheduling Agent
- Skill & Certification Agent
- Safety / EHS Agent
- Attendance & Leave Agent
- Quality Trace Agent
- Risk & Audit Agent

输出：

- 高风险排班项
- 风险原因
- 涉及员工、产线、工位和班次
- 替代人员建议
- 是否允许发布
- 必须人工确认的事项

## 14. 与现有模块的衔接

| 现有模块 | 制造场景扩展方向 |
| --- | --- |
| employee | 班组归属、产线支援、岗位资质、设备授权 |
| department | 生产部门、车间、产线归属 |
| attendance | 排班出勤、缺勤补位、工时一致性校验 |
| leave | 请假对排班和产能的影响 |
| payroll | 加班、夜班津贴、计件、工序补贴 |
| employee_skill | 工位技能要求、跨线支援、技能缺口 |
| skill_catalog | 工序技能、设备技能、质量技能 |
| project | 可弱化为生产任务、改善项目或临时支援任务 |
| knowledge_base | SOP、安全规则、质量标准、设备操作规范 |
| agent_memory | 班组长偏好、历史调度习惯、常用产线规则 |

## 15. API 设计建议

### 15.1 班组、产线与工位 API

```text
POST   /production-lines
GET    /production-lines
POST   /production-teams
GET    /production-teams
POST   /workstations
GET    /workstations
POST   /employee-team-assignments
GET    /employees/{employee_id}/production-profile
```

### 15.2 排班 API

```text
POST   /shifts
GET    /shifts
POST   /production-shift-plans
GET    /production-shift-plans
POST   /shift-assignments
POST   /shift-change-requests
POST   /production-shift-plans/{plan_id}/agent-review
```

### 15.3 资质与授权 API

```text
POST   /certifications
GET    /certifications
POST   /employee-certifications
GET    /employees/{employee_id}/certifications
POST   /equipment-authorizations
GET    /employees/{employee_id}/equipment-authorizations
POST   /employees/{employee_id}/workstation-eligibility-check
```

### 15.4 安全与质量 API

```text
POST   /safety-trainings
POST   /employee-safety-records
GET    /employees/{employee_id}/safety-status
POST   /quality-incidents
GET    /quality-incidents
POST   /quality-incidents/{incident_id}/agent-analysis
```

### 15.5 风险 API

```text
POST   /production-risk-signals
GET    /production-risk-signals
POST   /production-risk-signals/{risk_id}/reviews
POST   /production-risks/detect
POST   /production-risks/agent-assessment
```

## 16. Skill 设计建议

| Skill | 典型工具 |
| --- | --- |
| production_staffing | query_line_staffing、find_support_workers、analyze_staffing_gap |
| shift_scheduling | query_shift_plan、assign_shift、find_replacement_worker、review_shift_plan |
| certification_management | check_workstation_eligibility、query_employee_certifications、detect_expiring_certifications |
| safety_compliance | query_safety_training_status、check_ehs_compliance、detect_safety_risks |
| production_worklog | query_work_logs、compare_attendance_and_worklog、analyze_overtime_risk |
| quality_trace | query_quality_incidents、analyze_personnel_factors、suggest_corrective_actions |
| labor_cost | estimate_shift_labor_cost、analyze_overtime_cost、review_piecework_records |
| production_risk | detect_production_risks、review_risk_signal、suggest_mitigation_actions |

## 17. Multi-Agent 编排策略

### 17.1 轻量编排

适合第一阶段：

```text
Coordinator Agent
  -> Domain Skill Tools
  -> Risk & Audit Agent
  -> Final Suggestion
```

适合任务：

- 排班风险检查
- 工位上岗资格校验
- 简单缺勤补位
- 资质到期提醒

### 17.2 专业 Agent 编排

适合第二阶段：

```text
Coordinator Agent
  -> Shift Scheduling Agent
  -> Skill & Certification Agent
  -> Attendance & Leave Agent
  -> Safety / EHS Agent
  -> Risk & Audit Agent
```

适合任务：

- 复杂排班
- 跨线支援
- 加班安排
- 高风险工位人员调整

### 17.3 追溯型编排

适合质量和安全事件：

```text
Coordinator Agent
  -> Quality Trace Agent
  -> Production Staffing Agent
  -> Skill & Certification Agent
  -> Knowledge / SOP Agent
  -> Risk & Audit Agent
  -> Human Confirmation
```

适合任务：

- 质量异常人员因素分析
- 安全事件复盘
- 工位操作违规分析

## 18. 推荐落地路线

### 18.1 第一阶段：产线、班组、工位和资质

目标：

- 建立生产现场基础对象
- 支持员工与班组、产线、工位关联
- 支持技能、资质和设备授权校验

优先功能：

- production_lines
- production_teams
- workstations
- certifications
- employee_certifications
- equipment_authorizations

优先 Agent：

- Production Staffing Agent
- Skill & Certification Agent
- Knowledge / SOP Agent

### 18.2 第二阶段：排班、调班和加班

目标：

- 支持按产线、班次、工位排班
- 支持缺勤补位和调班
- 支持排班发布前 Agent 复核

优先功能：

- shift_definitions
- production_shift_plans
- employee_shift_assignments
- shift_change_requests
- overtime_requests

优先 Agent：

- Shift Scheduling Agent
- Attendance & Leave Agent
- Safety / EHS Agent
- Risk & Audit Agent

### 18.3 第三阶段：安全、质量和工时薪酬

目标：

- 支持安全培训和 EHS 合规
- 支持质量异常人员追溯
- 支持工时、计件和薪资核算前复核

优先功能：

- safety_trainings
- employee_safety_records
- quality_incidents
- production_work_logs
- piecework_records

优先 Agent：

- Safety / EHS Agent
- Quality Trace Agent
- Payroll / Labor Cost Agent

### 18.4 第四阶段：现场风险预警

目标：

- 自动发现排班、资质、加班、质量和安全风险
- 建立风险复核和处理闭环

优先功能：

- production_risk_signals
- production_risk_reviews
- staffing_gap_analyses

优先 Agent：

- Risk & Audit Agent
- Coordinator Agent

## 19. 最小可行版本

建议第一个版本只做以下内容：

### 19.1 新增业务

- 产线管理
- 班组管理
- 工位管理
- 员工资质管理
- 设备授权管理
- 排班计划基础能力
- 排班发布前风险复核

### 19.2 新增 Agent 能力

- Coordinator Agent
- Production Staffing Agent
- Skill & Certification Agent
- Safety / EHS Agent
- Risk & Audit Agent

### 19.3 新增 Skill

- production_staffing
- shift_scheduling
- certification_management
- safety_compliance
- production_risk

### 19.4 示例流程：排班发布前复核

1. 班组长创建明天排班计划
2. Coordinator Agent 识别为排班复核任务
3. Shift Scheduling Agent 检查班次和人员数量
4. Skill & Certification Agent 检查工位资质
5. Attendance & Leave Agent 检查请假和缺勤风险
6. Safety / EHS Agent 检查安全培训和高风险工位限制
7. Risk & Audit Agent 输出风险项和替代建议
8. 班组长人工确认后发布排班

## 20. 设计原则

- 项目定位优先服务工厂生产制造人员管理
- 简单员工信息维护不引入 multi-agent
- 排班、上岗、加班、质量追溯等高风险场景优先引入 multi-agent
- Agent 只给建议，高风险动作必须人工确认
- 所有风险判断需要保存依据和审计记录
- 安全、资质、设备授权优先级高于产能优化
- SOP 和安全制度应通过 Knowledge / SOP Agent 参与决策
- 专业 Agent 只负责自己的业务边界
- Coordinator Agent 负责汇总和协调，不替代专业判断

## 21. 总结

如果项目定位为工厂生产制造人员管理，multi-agent 的最佳切入点不是通用招聘、办公绩效或员工关系，而是生产现场的复杂协同：

- 谁能上哪条产线
- 谁能操作哪个设备
- 谁能补哪个班
- 哪些排班存在安全或资质风险
- 哪些质量异常可能与人员安排有关
- 当前产能是否受人力、技能或请假影响

推荐路线：

```text
产线 / 班组 / 工位
  -> 技能资质 / 设备授权
  -> 排班 / 调班 / 加班
  -> 安全培训 / EHS 合规
  -> 工时 / 计件 / 薪资复核
  -> 质量异常人员追溯
  -> 现场风险预警
```

沿着这条路线扩展后，multi-agent 会自然服务于生产现场决策，而不是停留在通用助手层面。
