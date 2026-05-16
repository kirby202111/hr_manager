# 工厂生产制造人员管理后端业务功能拆分

## 1. 目标

本文档从 `multi_agent_business_expansion_design.md` 中抽取出 multi-agent 所依赖的后端业务能力，作为先实现后端业务、后实现 Agent 能力的开发路线。

本文档只关注后端业务功能，不包含 multi-agent 编排、Agent 提示词、Agent 路由和 Agent 协作实现。

## 2. 设计原则

- 先补业务数据，再接入 Agent
- 先实现生产现场核心对象，再实现复杂分析
- 先保证规则可计算，再让 Agent 做解释和建议
- 高风险业务先保留人工确认字段和审计记录
- 后端接口应尽量结构化，方便后续 Agent 调用
- 优先复用当前项目已有的 models、schemas、repositories、services、routers 分层
- 保留现有 `attendance` 作为自然日考勤汇总，不改为按班次唯一
- 员工资质独立建模，不再依赖 `employee_skills.certification`
- 制造任务使用 `production_orders`，不复用现有 `project` 模块表达生产订单
- 工位所需技能、资质、设备使用关系表建模，不使用 JSON/text 作为主存储

## 3. 后端功能总览

建议按以下顺序实现：

1. 产线、班组、工位管理
2. 员工生产档案
3. 技能资质与设备授权
4. 安全培训与 EHS 记录
5. 生产订单
6. 生产排班与调班
7. 加班、工时与计件记录
8. 生产人力需求与缺口分析
9. 质量异常与人员追溯
10. 现场风险信号与复核记录

## 4. 与现有模型的决策结果

| 决策项 | 结论 |
| --- | --- |
| 部门与产线关系 | 保留 `departments` 表示组织部门或车间，新增 `production_lines` 表示产线 |
| 员工生产属性 | 保持 `employees` 极简，生产属性放入 `employee_production_profiles` 和 `employee_team_assignments` |
| 考勤与班次 | 保留现有 `attendance` 的 `(employee_id, date)` 唯一约束，表示自然日考勤汇总；班次和工位信息放入排班与工时模块 |
| 技能与资质 | 废弃 `employee_skills.certification` 的业务含义，员工资质统一使用 `employee_certifications` |
| 生产任务 | 不使用现有 `project` 表承载生产订单，新增 `production_orders` |
| 薪资与制造明细 | 保留 `payrolls` 作为月度汇总，加班、工时、计件作为薪资来源明细 |
| 工位要求 | 使用关系表维护工位所需技能、资质、设备，不用 JSON/text 字段作为主存储 |

## 5. 模块一：产线、班组、工位管理

### 4.1 业务说明

建立制造现场的基础组织结构，用于描述员工在哪条产线、哪个班组、哪些工位工作。

### 4.2 数据模型

#### production_lines

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| name | str | 产线名称 |
| department_id | int | 所属部门 |
| supervisor_employee_id | int, nullable | 产线负责人 |
| status | str | active、paused、inactive |
| description | str, nullable | 描述 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

#### production_teams

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| name | str | 班组名称 |
| line_id | int | 默认产线 |
| leader_employee_id | int, nullable | 班组长 |
| shift_type | str | day、night、rotating |
| status | str | active、inactive |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

#### workstations

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| line_id | int | 所属产线 |
| code | str | 工位编码 |
| name | str | 工位名称 |
| risk_level | str | low、medium、high |
| status | str | active、inactive |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

#### workstation_required_skills

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| workstation_id | int | 工位 ID |
| skill_id | int | 技能 ID |
| required_proficiency | str | beginner、intermediate、advanced、expert |
| created_at | datetime | 创建时间 |

#### workstation_required_certifications

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| workstation_id | int | 工位 ID |
| certification_id | int | 资质 ID |
| required | bool | 是否必需 |
| created_at | datetime | 创建时间 |

#### workstation_equipment_requirements

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| workstation_id | int | 工位 ID |
| equipment_code | str | 设备编码 |
| required_authorization_level | str | observer、operator、maintainer |
| created_at | datetime | 创建时间 |

### 4.3 服务能力

- 创建、查询、更新产线
- 创建、查询、更新班组
- 创建、查询、更新工位
- 查询某产线下的班组和工位
- 查询某工位所需技能、资质和设备
- 维护工位所需技能
- 维护工位所需资质
- 维护工位所需设备授权等级

### 4.4 API 建议

```text
POST   /production-lines
GET    /production-lines
GET    /production-lines/{line_id}
PATCH  /production-lines/{line_id}

POST   /production-teams
GET    /production-teams
GET    /production-teams/{team_id}
PATCH  /production-teams/{team_id}

POST   /workstations
GET    /workstations
GET    /workstations/{workstation_id}
PATCH  /workstations/{workstation_id}
GET    /production-lines/{line_id}/workstations

POST   /workstations/{workstation_id}/required-skills
GET    /workstations/{workstation_id}/required-skills
DELETE /workstations/{workstation_id}/required-skills/{requirement_id}

POST   /workstations/{workstation_id}/required-certifications
GET    /workstations/{workstation_id}/required-certifications
DELETE /workstations/{workstation_id}/required-certifications/{requirement_id}

POST   /workstations/{workstation_id}/equipment-requirements
GET    /workstations/{workstation_id}/equipment-requirements
DELETE /workstations/{workstation_id}/equipment-requirements/{requirement_id}
```

## 6. 模块二：员工生产档案

### 5.1 业务说明

在现有员工信息基础上，补充生产现场所需的员工属性，例如默认班组、可支援产线、是否一线员工、生产状态等。

### 5.2 数据模型

#### employee_team_assignments

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| employee_id | int | 员工 ID |
| team_id | int | 班组 ID |
| line_id | int | 产线 ID |
| start_date | date | 开始日期 |
| end_date | date, nullable | 结束日期 |
| is_primary | bool | 是否主班组 |
| created_at | datetime | 创建时间 |

#### employee_production_profiles

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| employee_id | int | 员工 ID |
| worker_type | str | operator、inspector、technician、team_leader |
| production_status | str | active、inactive、restricted |
| can_support_lines | JSON/text | 可支援产线 ID 列表 |
| notes | str, nullable | 备注 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 5.3 服务能力

- 设置员工主班组
- 维护员工可支援产线
- 查询员工生产档案
- 查询班组成员
- 查询产线可用人员池

### 5.4 API 建议

```text
POST   /employee-team-assignments
GET    /employee-team-assignments
GET    /production-teams/{team_id}/employees
GET    /production-lines/{line_id}/available-employees

POST   /employee-production-profiles
GET    /employees/{employee_id}/production-profile
PATCH  /employees/{employee_id}/production-profile
```

## 7. 模块三：技能资质与设备授权

### 6.1 业务说明

将“员工掌握技能”和“员工被允许上岗”区分开。制造现场中，某员工即使具备技能，也可能因为资质过期、安全培训未完成或设备授权不足而不能上岗。

现有 `employee_skills.certification` 字段不再作为正式资质来源。后续实现时可以保留字段用于历史兼容或展示备注，但业务校验必须以 `employee_certifications` 为准。

### 6.2 数据模型

#### certifications

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| name | str | 资质名称 |
| category | str | safety、equipment、process、quality |
| required_training_hours | float | 所需培训学时 |
| validity_months | int, nullable | 有效期月数 |
| description | str, nullable | 描述 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

#### employee_certifications

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| employee_id | int | 员工 ID |
| certification_id | int | 资质 ID |
| issued_at | date | 发证日期 |
| expires_at | date, nullable | 到期日期 |
| status | str | valid、expired、revoked |
| evidence | str, nullable | 证明材料 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

#### equipment_authorizations

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| employee_id | int | 员工 ID |
| equipment_code | str | 设备编码 |
| authorization_level | str | observer、operator、maintainer |
| issued_at | date | 授权日期 |
| expires_at | date, nullable | 到期日期 |
| status | str | valid、expired、revoked |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 6.3 服务能力

- 创建资质定义
- 给员工添加资质
- 给员工添加设备授权
- 查询员工资质和设备授权
- 检查员工是否满足工位上岗要求
- 检查即将过期的资质和授权

### 6.4 核心业务规则

工位上岗资格校验至少包含：

- 员工生产状态为 active
- 员工具备工位要求的技能
- 员工具备工位要求的有效资质
- 员工具备相关设备有效授权
- 高风险工位需要额外检查安全培训记录

技能来源使用现有 `employee_skills` 和 `skill_catalogs`；资质来源使用新增 `employee_certifications`；设备授权来源使用新增 `equipment_authorizations`。

### 6.5 API 建议

```text
POST   /certifications
GET    /certifications
GET    /certifications/{certification_id}
PATCH  /certifications/{certification_id}

POST   /employee-certifications
GET    /employees/{employee_id}/certifications
PATCH  /employee-certifications/{employee_certification_id}

POST   /equipment-authorizations
GET    /employees/{employee_id}/equipment-authorizations
PATCH  /equipment-authorizations/{authorization_id}

POST   /employees/{employee_id}/workstation-eligibility-check
GET    /certifications/expiring
GET    /equipment-authorizations/expiring
```

## 8. 模块四：安全培训与 EHS 记录

### 7.1 业务说明

安全培训是高风险工位上岗、夜班、特殊设备操作和安全事件复盘的重要依据。

### 7.2 数据模型

#### safety_trainings

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| title | str | 培训名称 |
| category | str | general、line、equipment、hazard |
| required_for_certification_id | int, nullable | 关联资质 |
| validity_months | int, nullable | 有效期 |
| description | str, nullable | 描述 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

#### employee_safety_records

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| employee_id | int | 员工 ID |
| training_id | int | 培训 ID |
| completed_at | date | 完成时间 |
| score | float, nullable | 考试成绩 |
| expires_at | date, nullable | 到期日期 |
| status | str | valid、expired、failed |
| created_at | datetime | 创建时间 |

#### safety_incidents

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| employee_id | int, nullable | 相关员工 |
| line_id | int, nullable | 产线 |
| workstation_id | int, nullable | 工位 |
| incident_date | date | 发生日期 |
| severity | str | low、medium、high、critical |
| summary | str | 摘要 |
| status | str | open、reviewed、closed |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 7.3 服务能力

- 创建安全培训
- 记录员工培训完成情况
- 查询员工安全培训状态
- 查询过期或即将过期的安全培训
- 记录安全事件
- 查询员工安全事件历史

### 7.4 API 建议

```text
POST   /safety-trainings
GET    /safety-trainings
PATCH  /safety-trainings/{training_id}

POST   /employee-safety-records
GET    /employees/{employee_id}/safety-records
GET    /employees/{employee_id}/safety-status
GET    /safety-records/expiring

POST   /safety-incidents
GET    /safety-incidents
GET    /safety-incidents/{incident_id}
PATCH  /safety-incidents/{incident_id}
```

## 9. 模块五：生产订单

### 9.1 业务说明

生产订单用于描述制造现场的生产任务。它替代通用 `project` 在制造场景中的任务承载职责，避免将项目管理语义和生产订单语义混在一起。

`project` 模块可以继续保留用于改善项目、临时专项或研发类协作，但生产排班、产能、人力缺口、质量追溯应优先关联 `production_orders`。

### 9.2 数据模型

#### production_orders

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| order_no | str | 生产订单号 |
| product_name | str | 产品名称 |
| line_id | int, nullable | 计划产线 |
| planned_quantity | int | 计划数量 |
| planned_start_date | date, nullable | 计划开始日期 |
| planned_end_date | date, nullable | 计划结束日期 |
| status | str | planned、running、paused、completed、cancelled |
| priority | str | low、normal、high、urgent |
| description | str, nullable | 描述 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

#### production_order_operations

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| order_id | int | 生产订单 ID |
| workstation_id | int | 工位 ID |
| process_code | str | 工序编码 |
| sequence | int | 工序顺序 |
| planned_hours | float, nullable | 计划工时 |
| required_headcount | int | 所需人数 |
| status | str | planned、running、completed |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 9.3 服务能力

- 创建生产订单
- 查询生产订单
- 更新生产订单状态
- 维护生产订单工序
- 查询订单所需工位、人力和技能资质
- 为排班、人力缺口和质量追溯提供订单上下文

### 9.4 API 建议

```text
POST   /production-orders
GET    /production-orders
GET    /production-orders/{order_id}
PATCH  /production-orders/{order_id}

POST   /production-orders/{order_id}/operations
GET    /production-orders/{order_id}/operations
PATCH  /production-order-operations/{operation_id}

GET    /production-orders/{order_id}/staffing-context
```

## 10. 模块六：生产排班与调班

### 8.1 业务说明

排班是后续 multi-agent 的核心业务底座。它将产线、班次、工位、员工、技能资质、请假和考勤连接起来。

### 8.2 数据模型

#### shift_definitions

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| code | str | 班次编码 |
| name | str | 班次名称 |
| start_time | time | 开始时间 |
| end_time | time | 结束时间 |
| shift_type | str | day、night、overtime |
| allowance_rate | float | 班次津贴系数 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

#### production_shift_plans

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| order_id | int, nullable | 关联生产订单 |
| line_id | int | 产线 ID |
| shift_id | int | 班次 ID |
| work_date | date | 日期 |
| required_headcount | int | 所需人数 |
| status | str | draft、published、adjusted、closed |
| created_by | str, nullable | 创建人 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

#### employee_shift_assignments

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| plan_id | int | 排班计划 ID |
| employee_id | int | 员工 ID |
| workstation_id | int | 工位 ID |
| assignment_type | str | normal、support、overtime、replacement |
| status | str | planned、confirmed、cancelled |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

#### shift_change_requests

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| employee_id | int | 员工 ID |
| original_assignment_id | int | 原排班 |
| target_assignment_id | int, nullable | 目标排班 |
| reason | str | 调班原因 |
| status | str | pending、approved、rejected |
| risk_level | str | low、medium、high |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 8.3 服务能力

- 创建班次定义
- 创建产线排班计划
- 给排班计划分配员工和工位
- 查询某日、某产线、某班次排班
- 查询员工个人排班
- 创建调班申请
- 审批调班申请
- 发布排班
- 关闭已完成排班

### 8.4 核心业务规则

发布排班前应支持后端校验：

- 排班人数是否满足 required_headcount
- 员工是否请假
- 员工是否已被其他班次占用
- 员工是否满足工位技能和资质要求
- 员工是否具备设备授权
- 员工是否存在安全培训过期
- 是否存在连续夜班或超时风险

注意：这里不修改现有 `attendance` 表的自然日考勤汇总模型。排班冲突和同日多班次由 `employee_shift_assignments` 判断；实际生产工时由 `production_work_logs` 记录。

### 8.5 API 建议

```text
POST   /shifts
GET    /shifts
PATCH  /shifts/{shift_id}

POST   /production-shift-plans
GET    /production-shift-plans
GET    /production-shift-plans/{plan_id}
PATCH  /production-shift-plans/{plan_id}
POST   /production-shift-plans/{plan_id}/publish
POST   /production-shift-plans/{plan_id}/validate

POST   /shift-assignments
GET    /shift-assignments
PATCH  /shift-assignments/{assignment_id}

POST   /shift-change-requests
GET    /shift-change-requests
POST   /shift-change-requests/{request_id}/approve
POST   /shift-change-requests/{request_id}/reject
```

## 11. 模块七：加班、工时与计件记录

### 9.1 业务说明

制造场景中的薪资和成本计算依赖加班、班次、工时、产量和计件记录。该模块先提供业务数据，后续再接入薪资复核 Agent。

### 9.2 数据模型

#### overtime_requests

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| employee_id | int | 员工 ID |
| line_id | int | 产线 ID |
| work_date | date | 日期 |
| hours | float | 加班小时 |
| reason | str | 原因 |
| status | str | pending、approved、rejected |
| risk_level | str | low、medium、high |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

#### production_work_logs

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| order_id | int, nullable | 生产订单 ID |
| employee_id | int | 员工 ID |
| line_id | int | 产线 ID |
| workstation_id | int | 工位 ID |
| work_date | date | 日期 |
| shift_id | int | 班次 ID |
| hours | float | 工时 |
| output_quantity | int | 产量 |
| defect_quantity | int | 不良数 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

#### piecework_records

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| employee_id | int | 员工 ID |
| process_code | str | 工序编码 |
| quantity | int | 数量 |
| unit_rate | float | 单价 |
| work_date | date | 日期 |
| source_log_id | int, nullable | 来源工时记录 |
| created_at | datetime | 创建时间 |

### 9.3 服务能力

- 创建加班申请
- 审批加班申请
- 记录生产工时
- 记录产量和不良数
- 记录计件数据
- 查询员工月度工时
- 查询产线工时和产量
- 比对考勤和工时是否一致

考勤与工时比对以现有 `attendance` 的自然日汇总为基础，和 `production_work_logs` 的同日工时汇总进行比较。

### 9.4 API 建议

```text
POST   /overtime-requests
GET    /overtime-requests
POST   /overtime-requests/{request_id}/approve
POST   /overtime-requests/{request_id}/reject

POST   /production-work-logs
GET    /production-work-logs
GET    /employees/{employee_id}/production-work-logs
GET    /production-lines/{line_id}/production-work-logs

POST   /piecework-records
GET    /piecework-records
GET    /employees/{employee_id}/piecework-records

GET    /employees/{employee_id}/monthly-work-summary
GET    /production-work-logs/attendance-comparison
```

## 12. 模块八：生产人力需求与缺口分析

### 10.1 业务说明

生产主管和班组长需要知道某天某班次是否缺人、缺技能、缺资质。该模块为后续智能排班和人员推荐提供基础。

### 10.2 数据模型

#### staffing_requirements

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| order_id | int, nullable | 生产订单 ID |
| line_id | int | 产线 ID |
| workstation_id | int | 工位 ID |
| shift_id | int | 班次 ID |
| work_date | date | 日期 |
| required_headcount | int | 所需人数 |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

#### staffing_requirement_skills

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| requirement_id | int | 人力需求 ID |
| skill_id | int | 技能 ID |
| required_proficiency | str | 所需熟练度 |
| created_at | datetime | 创建时间 |

#### staffing_requirement_certifications

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| requirement_id | int | 人力需求 ID |
| certification_id | int | 资质 ID |
| created_at | datetime | 创建时间 |

#### staffing_gap_analyses

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| line_id | int | 产线 ID |
| work_date | date | 日期 |
| shift_id | int | 班次 ID |
| gap_summary | str | 缺口摘要 |
| suggestions | JSON/text | 建议 |
| created_by | str | human、system、agent |
| created_at | datetime | 创建时间 |

### 10.3 服务能力

- 创建工位人力需求
- 查询某日、某产线、某班次人力需求
- 根据排班计算人力缺口
- 根据员工技能和资质计算技能/资质缺口
- 维护人力需求所需技能
- 维护人力需求所需资质
- 保存缺口分析结果
- 查询可支援人员候选列表

### 10.4 API 建议

```text
POST   /staffing-requirements
GET    /staffing-requirements
PATCH  /staffing-requirements/{requirement_id}

POST   /staffing-gap-analyses/run
GET    /staffing-gap-analyses
GET    /staffing-gap-analyses/{analysis_id}
GET    /production-lines/{line_id}/support-candidates
```

## 13. 模块九：质量异常与人员追溯

### 11.1 业务说明

质量异常不仅是质量模块问题，也可能与人员安排、技能、资质、培训、疲劳和跨线支援有关。该模块先记录质量异常和关联人员，为后续分析提供数据。

### 11.2 数据模型

#### quality_incidents

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| order_id | int, nullable | 生产订单 ID |
| line_id | int | 产线 |
| workstation_id | int | 工位 |
| shift_id | int | 班次 |
| incident_date | date | 日期 |
| defect_type | str | 缺陷类型 |
| defect_quantity | int | 缺陷数量 |
| severity | str | low、medium、high、critical |
| summary | str | 摘要 |
| status | str | open、reviewed、closed |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

#### quality_incident_employees

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| incident_id | int | 质量异常 ID |
| employee_id | int | 员工 ID |
| role | str | operator、inspector、team_leader |
| note | str, nullable | 说明 |
| created_at | datetime | 创建时间 |

#### corrective_actions

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| incident_id | int | 质量异常 ID |
| owner_employee_id | int | 负责人 |
| action | str | 整改动作 |
| due_date | date | 截止日期 |
| status | str | open、done、cancelled |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 11.3 服务能力

- 创建质量异常
- 关联质量异常涉及员工
- 查询某产线、工位、班次的质量异常
- 查询员工相关质量异常
- 创建整改动作
- 更新整改动作状态
- 生成质量异常基础追溯数据
- 关联生产订单，支持按订单追溯质量异常

### 11.4 API 建议

```text
POST   /quality-incidents
GET    /quality-incidents
GET    /quality-incidents/{incident_id}
PATCH  /quality-incidents/{incident_id}

POST   /quality-incidents/{incident_id}/employees
GET    /quality-incidents/{incident_id}/employees

POST   /quality-incidents/{incident_id}/corrective-actions
GET    /quality-incidents/{incident_id}/corrective-actions
PATCH  /corrective-actions/{action_id}

GET    /quality-incidents/{incident_id}/trace-context
```

## 14. 模块十：现场风险信号与复核记录

### 12.1 业务说明

风险信号模块用于沉淀后端规则校验和后续 Agent 分析的结果。即使暂时不接 Agent，也可以先由系统规则生成风险。

### 12.2 数据模型

#### production_risk_signals

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| order_id | int, nullable | 生产订单 ID |
| employee_id | int, nullable | 员工 ID |
| line_id | int, nullable | 产线 ID |
| workstation_id | int, nullable | 工位 ID |
| shift_assignment_id | int, nullable | 排班 ID |
| signal_type | str | 风险类型 |
| severity | str | low、medium、high、critical |
| evidence | JSON/text | 证据 |
| status | str | open、reviewed、resolved、ignored |
| detected_by | str | human、system、agent |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

#### production_risk_reviews

| 字段 | 类型建议 | 说明 |
| --- | --- | --- |
| id | int | 主键 |
| risk_signal_id | int | 风险信号 ID |
| reviewer | str | 复核人或来源 |
| conclusion | str | 复核结论 |
| action_suggestion | str | 处理建议 |
| created_at | datetime | 创建时间 |

### 12.3 风险类型建议

- uncertified_worker_assigned：未认证人员上岗
- expired_certification：资质过期
- expired_safety_training：安全培训过期
- missing_equipment_authorization：缺少设备授权
- leave_conflict：排班与请假冲突
- shift_conflict：员工同日班次冲突
- insufficient_headcount：排班人数不足
- excessive_overtime：加班超时
- consecutive_night_shift：连续夜班
- quality_personnel_risk：质量异常人员因素风险
- attendance_worklog_mismatch：考勤与工时不一致

### 12.4 服务能力

- 创建风险信号
- 查询风险信号
- 更新风险状态
- 创建风险复核记录
- 排班发布前生成风险信号
- 工位上岗校验生成风险信号
- 工时与考勤比对生成风险信号
- 生产订单关联的排班、人力和质量风险生成风险信号

### 12.5 API 建议

```text
POST   /production-risk-signals
GET    /production-risk-signals
GET    /production-risk-signals/{risk_id}
PATCH  /production-risk-signals/{risk_id}

POST   /production-risk-signals/{risk_id}/reviews
GET    /production-risk-signals/{risk_id}/reviews

POST   /production-risks/detect/shift-plan/{plan_id}
POST   /production-risks/detect/workstation-eligibility
POST   /production-risks/detect/attendance-worklog
```

## 15. 建议实现顺序

### 13.1 第一阶段：生产现场基础对象

实现模块：

- 产线管理
- 班组管理
- 工位管理
- 员工生产档案

产出：

- 数据模型
- CRUD API
- 基础测试
- 种子数据

### 15.2 第二阶段：资质、安全和设备授权

实现模块：

- 资质定义
- 员工资质
- 设备授权
- 安全培训记录

产出：

- 工位上岗资格校验服务
- 资质过期查询
- 安全培训状态查询

### 15.3 第三阶段：生产订单、排班与调班

实现模块：

- 生产订单
- 订单工序
- 班次定义
- 生产排班计划
- 员工排班分配
- 调班申请

产出：

- 排班发布前校验
- 请假冲突校验
- 工位资格校验接入排班

### 15.4 第四阶段：工时、加班和计件

实现模块：

- 加班申请
- 生产工时记录
- 计件记录

产出：

- 月度工时汇总
- 考勤与工时比对
- 加班风险基础校验

### 15.5 第五阶段：缺口分析、质量追溯和风险信号

实现模块：

- 人力需求
- 缺口分析
- 质量异常
- 风险信号
- 风险复核

产出：

- 排班风险信号
- 质量异常追溯上下文
- 人力和资质缺口分析

## 16. 后续 Agent 接入预留点

虽然本文档不实现 Agent，但后端应预留以下能力：

- 所有复杂校验服务返回结构化结果
- 风险信号保存 evidence 字段
- 审核、发布、审批动作保留人工确认状态
- 关键业务提供 summary 或 context API
- 列表查询支持按日期、产线、班次、员工筛选
- 高风险动作不要在后端默认自动执行

建议重点预留的上下文 API：

```text
GET /employees/{employee_id}/production-profile
GET /employees/{employee_id}/workstation-eligibility-context
GET /production-orders/{order_id}/staffing-context
GET /production-shift-plans/{plan_id}/validation-context
GET /quality-incidents/{incident_id}/trace-context
GET /production-lines/{line_id}/staffing-context
GET /production-risk-signals/{risk_id}/context
```

## 17. 最小可行版本

如果希望快速打好 multi-agent 业务基础，建议 MVP 只做：

- production_lines
- production_teams
- workstations
- employee_team_assignments
- employee_production_profiles
- certifications
- employee_certifications
- equipment_authorizations
- safety_trainings
- employee_safety_records
- production_orders
- production_order_operations
- shift_definitions
- production_shift_plans
- employee_shift_assignments
- production_risk_signals
- production_risk_reviews

MVP 必须具备的业务能力：

- 创建产线、班组、工位
- 给员工分配班组和产线
- 维护员工资质和设备授权
- 维护员工安全培训记录
- 创建生产订单和订单工序
- 创建排班计划
- 分配员工到工位
- 校验排班中的资格、安全和请假冲突
- 生成风险信号
- 人工复核风险信号

## 18. 总结

当前阶段建议先实现制造现场人员管理的后端业务底座，不急于实现 multi-agent。

后端优先级应围绕：

```text
产线 / 班组 / 工位
  -> 员工生产档案
  -> 技能资质 / 设备授权
  -> 安全培训
  -> 生产订单
  -> 排班 / 调班
  -> 工时 / 加班 / 计件
  -> 人力缺口 / 质量追溯 / 风险信号
```

当这些业务数据和规则具备后，后续 Agent 才能真正做有价值的判断，而不是停留在泛泛的文本建议。
