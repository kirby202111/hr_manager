# 项目实体建模与功能方法设计文档

## 1. 文档目的

本文档面向当前 `workforce-ops` 后端代码，梳理项目中已经落地的实体模型、实体之间的关系，以及围绕这些实体提供的服务方法。目标是让开发者可以快速理解：

- 当前项目的领域边界是什么
- 每个实体在数据库中的职责和关键字段是什么
- 各实体之间如何关联
- 对每个实体，系统已经提供了哪些业务方法
- 后续新增 API、Agent Skill 或报表时，应该落在哪一层

本文档以当前代码中的现行实现为准，主要参考：

- `app/models/*`
- `app/services/*`
- `app/repositories/*`
- `app/schemas/*`


## 2. 总体设计视图

### 2.1 分层结构

当前项目基本采用如下分层：

```text
Router -> Service -> Repository -> Model/Database
```

其中：

- `models` 负责实体表结构定义
- `repositories` 负责通用 CRUD 与查询聚合
- `services` 负责业务校验、状态流转、跨实体协同
- `schemas` 负责请求/响应模型
- `agent` 与 `knowledge_base` 在此基础上扩展智能能力

### 2.2 当前领域划分

从代码来看，项目已经从传统 HR 命名逐步迁移到制造现场导向的领域模型，可分为四组：

1. 基础组织与员工主数据
2. 生产现场结构与人员画像
3. 出勤、请假、薪资、项目等协同业务
4. Agent 记忆与知识增强能力

### 2.3 命名映射说明

当前代码里有几组“文件名是新领域词，类名仍保留旧兼容名”的情况：

- `app/models/worker.py` 中实体类名是 `Employee`
- `app/models/org_unit.py` 中实体类名是 `Department`
- `app/models/skill_definition.py` 中实体类名是 `SkillCatalog`

这说明项目正在从通用 HR 模型向制造场景模型过渡。文档会同时使用“业务含义名”和“代码实体名”描述，避免阅读时混淆。


## 3. 核心建模原则

### 3.1 以员工主数据为基础，以产线现场为核心

`Employee` 和 `Department` 仍然是基础主数据入口，但系统核心能力已经延伸到：

- 产线 `ProductionLine`
- 班组 `ProductionTeam`
- 工位 `Workstation`
- 工单 `ProductionOrder`
- 排班 `ProductionShiftPlan`
- 工位资格、设备授权、安全培训、风险审查

### 3.2 轻关系、强服务校验

大部分表没有显式 SQLAlchemy 外键关系定义，而是在 Service 层通过：

- `exists(...)`
- `employee_exists(...)`
- `line_exists(...)`
- `workstation_exists(...)`

等方法完成引用完整性校验。也就是说，当前项目更依赖“业务服务层约束”，而不是 ORM 关系导航。

### 3.3 统一状态枚举在 Service 层维护

制造域状态值统一收敛在 `app/services/shopfloor_support.py` 的 `VALID` 字典中，例如：

- 产线状态
- 班组班次类型
- 风险等级
- 资格有效性
- 工单状态
- 排班状态
- 风险信号状态

这使得多数实体的状态约束集中在 Service 层而非 Model 层。


## 4. 实体关系总览

### 4.1 基础关系

```text
Department 1 -> N Employee
Employee 1 -> N EmployeeSkill
SkillCatalog 1 -> N EmployeeSkill
Employee 1 -> N Attendance
Employee 1 -> N Leave
Employee 1 -> N Payroll
```

### 4.2 生产现场关系

```text
Department 1 -> N ProductionLine
ProductionLine 1 -> N ProductionTeam
ProductionLine 1 -> N Workstation
Employee 1 -> N EmployeeTeamAssignment
Employee 1 -> 1 EmployeeProductionProfile
Workstation 1 -> N WorkstationRequiredSkill
Workstation 1 -> N WorkstationRequiredCertification
Workstation 1 -> N WorkstationEquipmentRequirement
```

### 4.3 资格、排班与风险关系

```text
Certification 1 -> N EmployeeCertification
SafetyTraining 1 -> N EmployeeSafetyRecord
ProductionOrder 1 -> N ProductionOrderOperation
ShiftDefinition 1 -> N ProductionShiftPlan
ProductionShiftPlan 1 -> N EmployeeShiftAssignment
ProductionRiskSignal 1 -> N ProductionRiskReview
```

### 4.4 项目协同关系

```text
Project 1 -> N ProjectSkillRequirement
Project 1 -> N ProjectMember
Project 1 -> N ProjectTimesheet
ProjectSkillRequirement 1 -> N ProjectTimesheet
Employee 1 -> N ProjectMember
Employee 1 -> N ProjectTimesheet
SkillCatalog 1 -> N ProjectSkillRequirement
```


## 5. 基础组织与员工主数据

### 5.1 Department / 部门

**代码位置**

- Model: `app/models/org_unit.py`
- Service: `app/services/org_unit.py`

**建模职责**

部门是组织归属与管理责任的最小管理单元，为员工、产线提供组织挂靠点。

**关键字段**

- `id`: 主键
- `name`: 部门名称，唯一
- `description`: 部门描述
- `manager`: 部门负责人

**约束**

- `name` 唯一约束

**关联关系**

- 一个部门可拥有多个员工
- 一个部门可拥有多条产线

**服务方法**

- `list_departments()`
  - 查询全部部门
  - 聚合员工数量
- `get_department(department_id)`
  - 查询单个部门详情
  - 返回部门下员工数
- `create_department(dept_in)`
  - 创建部门
  - 校验部门名称不可重复
- `update_department(department_id, dept_in)`
  - 更新部门
  - 校验名称冲突
- `delete_department(department_id)`
  - 删除部门
  - 若部门下仍有员工则禁止删除
- `get_department_employees(department_id)`
  - 查询部门下员工列表

**业务定位**

这是制造现场实体的组织根节点，主要承接员工和产线的归属，而不是复杂组织树。


### 5.2 Employee / 员工

**代码位置**

- Model: `app/models/worker.py`
- Service: `app/services/worker.py`

**建模职责**

员工是全系统最核心的被调度主体，也是考勤、请假、技能、排班、项目、薪资、安全记录等实体的统一中心。

**关键字段**

- `id`: 主键
- `name`: 员工姓名
- `department_id`: 所属部门
- `salary`: 基础薪资

**约束**

- `department_id` 建索引，支持按部门查询

**关联关系**

- 多条技能记录
- 多条考勤记录
- 多条请假记录
- 多条薪资记录
- 1 条生产画像
- 多条班组归属记录
- 多条资格、培训、排班、项目、风险相关记录

**服务方法**

- `list_employees()`
  - 列表查询
  - 自动补充 `department_name`
- `get_employee(employee_id)`
  - 查询单个员工详情
- `create_employee(employee_in)`
  - 创建员工
  - 若填写 `department_id`，会先校验部门存在
- `update_employee(employee_id, employee_in)`
  - 更新员工信息
  - 更新前校验员工与部门
- `delete_employee(employee_id)`
  - 删除员工

**业务定位**

当前 `Employee` 仍然是统一主档实体，后续如果继续制造化，可以在不破坏兼容性的前提下扩展更多基础属性，如工号、岗位序列、用工类型等。


### 5.3 SkillCatalog / 技能目录

**代码位置**

- Model: `app/models/skill_definition.py`
- Service: `app/services/skill_definition.py`

**建模职责**

技能目录定义“系统认可的技能标准项”，供员工技能、项目技能需求、工位技能要求引用。

**关键字段**

- `id`: 主键
- `name`: 技能名称，唯一
- `category`: 技能类别
- `description`: 技能说明
- `created_at`: 创建时间

**关联关系**

- 可被 `EmployeeSkill` 引用
- 可被 `ProjectSkillRequirement` 引用
- 可被 `WorkstationRequiredSkill` 引用

**服务方法**

- `list_skills(category=None)`
  - 查询技能目录
  - 返回每项技能被员工引用的人数
- `get_skill(skill_id)`
  - 查询单个技能
- `create_skill(skill_in)`
  - 创建技能目录项
  - 校验名称唯一
- `update_skill(skill_id, skill_in)`
  - 更新技能目录项
  - 校验名称冲突
- `delete_skill(skill_id)`
  - 删除技能目录项
  - 若已被员工技能或项目技能需求引用则禁止删除

**业务定位**

这是技能维度的主数据表，是制造业务里“能力要求”和“能力供给”对齐的基础。


### 5.4 EmployeeSkill / 员工技能

**代码位置**

- Model: `app/models/worker_skill.py`
- Service: `app/services/worker_skill.py`

**建模职责**

员工技能记录体现员工对某项技能的掌握情况，是工位资格校验、项目派工、跨线支援推荐的重要输入。

**关键字段**

- `id`: 主键
- `employee_id`: 员工 ID
- `skill_name`: 技能名称
- `skill_id`: 技能目录 ID，可为空
- `proficiency_level`: 熟练度
- `years_of_experience`: 经验年限
- `certification`: 相关证书说明
- `created_at`: 创建时间

**约束**

- `employee_id + skill_name` 唯一
- `employee_id`、`skill_id` 建索引
- 熟练度有效值：`beginner / intermediate / advanced / expert`

**关联关系**

- 属于某个员工
- 可选关联到技能目录

**服务方法**

- `list_skills()`
  - 查询全量员工技能
  - 自动补充员工名、技能类别
- `list_skills_by_employee(employee_id)`
  - 查询某员工的技能清单
- `list_employees_by_skill(skill_name)`
  - 反向按技能名查员工
- `get_skill(skill_id)`
  - 查询单条技能记录
- `create_skill(skill_in)`
  - 创建技能记录
  - 校验员工存在、熟练度有效、技能目录存在
- `update_skill(skill_id, skill_in)`
  - 更新技能记录
  - 继续校验熟练度与技能目录
- `delete_skill(skill_id)`
  - 删除技能记录

**业务定位**

这是“人具备什么能力”的事实表，后续可进一步扩展为技能评估历史或技能矩阵。


## 6. 出勤、请假与薪资

### 6.1 Attendance / 考勤

**代码位置**

- Model: `app/models/attendance.py`
- Service: `app/services/attendance.py`

**建模职责**

考勤记录按员工和日期记录上下班情况，并沉淀迟到、早退、工时等结果，用于薪资扣款、出勤统计和排班可用性判断。

**关键字段**

- `id`
- `employee_id`
- `date`
- `check_in`
- `check_out`
- `status`
- `work_hours`

**约束**

- `employee_id + date` 唯一
- `(employee_id, date)` 复合索引

**服务方法**

- `check_in(data)`
  - 员工签到
  - 防止同日重复签到
  - 自动计算初始考勤状态
- `check_out(record_id, data)`
  - 员工签退
  - 防止重复签退
  - 自动计算最终状态和工时
- `list_attendance(employee_id=None, start_date=None, end_date=None)`
  - 条件查询考勤记录
- `get_attendance(record_id)`
  - 查询单条考勤
- `get_employee_attendance(employee_id)`
  - 查询某员工全部考勤
- `get_employee_stats(employee_id, start_date, end_date)`
  - 汇总统计正常、迟到、早退、缺勤等指标

**业务定位**

当前模型偏“日级考勤”，适合与排班、薪资、缺勤分析联动。


### 6.2 Leave / 请假

**代码位置**

- Model: `app/models/leave.py`
- Service: `app/services/leave.py`

**建模职责**

请假记录用于管理员工休假申请与审批状态，是排班冲突校验和薪资扣款的重要输入。

**关键字段**

- `id`
- `employee_id`
- `leave_type`
- `leave_type_name`
- `start_date`
- `end_date`
- `days`
- `reason`
- `status`
- `approver`
- `approved_at`
- `created_at`

**约束**

- `(employee_id, status, start_date, end_date)` 复合索引

**内置业务规则**

- 结束日期不能早于开始日期
- 审批通过的假期不能时间重叠
- 部分假别受余额限制
- 只有 `pending` 状态可修改、审批、拒绝、取消

**服务方法**

- `create_leave(data)`
  - 创建请假申请
  - 校验员工存在、日期合法、假别合法、余额充足、无已批准假期冲突
- `list_leaves(employee_id=None, status=None)`
  - 条件查询请假单
- `get_leave(leave_id)`
  - 查询单条请假
- `update_leave(leave_id, data)`
  - 修改待审批请假
  - 重算天数并检查冲突
- `approve_leave(leave_id, approval)`
  - 审批通过
  - 再次校验日期冲突和余额
- `reject_leave(leave_id, approval)`
  - 审批拒绝
- `cancel_leave(leave_id)`
  - 取消待审批请假
- `get_leave_balance(employee_id)`
  - 计算员工各类假别总额、已用、剩余

**业务定位**

这是排班发布前的关键约束来源，`shift_staffing.validate_shift_plan()` 直接依赖已批准请假数据。


### 6.3 Payroll / 薪资

**代码位置**

- Model: `app/models/payroll.py`
- Service: `app/services/payroll.py`

**建模职责**

薪资实体承接月度薪资生成、草稿调整、支付确认与工资条汇总，当前重点覆盖基础工资、考勤扣款和事假扣款。

**关键字段**

- `id`
- `employee_id`
- `month`
- `base_salary`
- `bonuses`
- `deductions`
- `net_salary`
- `status`
- `payment_date`
- `created_at`

**约束**

- `employee_id + month` 唯一
- `(employee_id, month)` 复合索引

**核心计算逻辑**

- 净薪 = 基础工资 + 奖金 - 扣款
- 日薪按 `21.75` 工作日折算
- 迟到、早退按半天折算扣款
- 缺勤按整天折算扣款
- `personal` 事假按天扣款

**服务方法**

- `create_payroll(data)`
  - 手工创建某员工某月薪资草稿
- `generate_monthly_payroll(month)`
  - 批量为所有员工生成月度薪资
  - 自动计算考勤与请假扣款
- `list_payrolls(employee_id=None, month=None, status=None)`
  - 条件查询薪资单
- `get_payroll(payroll_id)`
  - 查询薪资单详情
- `update_payroll(payroll_id, data)`
  - 更新草稿薪资
  - 自动重算净薪
- `pay_payroll(payroll_id)`
  - 将草稿薪资置为已支付
- `get_employee_payrolls(employee_id)`
  - 查询员工薪资历史
- `get_payslip(payroll_id)`
  - 生成工资条视图
  - 汇总考勤、请假、扣款、奖金明细

**业务定位**

当前薪资模型是轻量版制造薪资核算，已经与考勤、请假联动，后续可继续扩展夜班津贴、加班费、工位补贴等。


## 7. 生产现场结构与人员画像

### 7.1 ProductionLine / 产线

**代码位置**

- Model: `app/models/shopfloor_structure.py`
- Service: `app/services/shopfloor_structure.py`

**建模职责**

产线是制造现场的人、班组、工位和排班计划的承载容器。

**关键字段**

- `id`
- `name`
- `department_id`
- `supervisor_employee_id`
- `status`
- `description`
- `created_at`
- `updated_at`

**状态值**

- `active`
- `paused`
- `inactive`

**服务方法**

- `create_line(data)`
  - 创建产线
  - 校验部门、主管员工和状态值
- `list_lines()`
  - 查询产线列表
- `get_line(line_id)`
  - 查询单条产线
- `update_line(line_id, data)`
  - 更新产线
  - 更新前校验状态值

**业务定位**

产线是后续班组、工位、工单、排班和风险汇总的第一层制造维度。


### 7.2 ProductionTeam / 班组

**代码位置**

- Model: `app/models/shopfloor_structure.py`
- Service: `app/services/shopfloor_structure.py`

**建模职责**

班组用于表达产线上的人力组织单元，与员工归属、换线支援、班次安排密切相关。

**关键字段**

- `id`
- `name`
- `line_id`
- `leader_employee_id`
- `shift_type`
- `status`
- `created_at`
- `updated_at`

**枚举约束**

- `shift_type`: `day / night / rotating`
- `status`: `active / inactive`

**服务方法**

- `create_team(data)`
  - 创建班组
  - 校验产线、班组长、班次类型、状态
- `get_team(team_id)`
  - 查询班组详情
- `update_team(team_id, data)`
  - 更新班组
  - 可重新挂到不同产线

**业务定位**

班组是员工现场归属与支援调度的直接组织层。


### 7.3 Workstation / 工位

**代码位置**

- Model: `app/models/shopfloor_structure.py`
- Service: `app/services/shopfloor_structure.py`

**建模职责**

工位定义了具体作业位置及其风险要求、资格要求和设备授权要求，是人员上岗资格判断的关键节点。

**关键字段**

- `id`
- `line_id`
- `code`
- `name`
- `risk_level`
- `status`
- `created_at`
- `updated_at`

**约束**

- `line_id + code` 唯一

**枚举约束**

- `risk_level`: `low / medium / high / critical`
- `status`: `active / inactive`

**服务方法**

- `create_workstation(data)`
  - 创建工位
  - 校验产线、风险等级、状态
- `get_workstation(workstation_id)`
  - 查询工位详情
- `update_workstation(workstation_id, data)`
  - 更新工位

**业务定位**

工位不是简单地点，而是“资格约束容器”。后续工位能否安排某员工，完全围绕该实体展开。


### 7.4 WorkstationRequiredSkill / 工位必备技能

**代码位置**

- Model: `app/models/shopfloor_structure.py`
- Service: `app/services/shopfloor_structure.py`

**建模职责**

用于定义某工位要求的技能和最低熟练度。

**关键字段**

- `id`
- `workstation_id`
- `skill_id`
- `required_proficiency`
- `created_at`

**服务方法**

- `add_required_skill(workstation_id, data)`
  - 为工位增加技能要求
  - 校验工位存在、技能目录存在、熟练度合法

**业务定位**

这是工位资格校验的第一类约束，`check_workstation_eligibility()` 会逐条校验。


### 7.5 WorkstationRequiredCertification / 工位必备资质

**代码位置**

- Model: `app/models/shopfloor_structure.py`
- Service: `app/services/shopfloor_structure.py`

**建模职责**

定义某工位要求的证书/资质项，以及是否为强制要求。

**关键字段**

- `id`
- `workstation_id`
- `certification_id`
- `required`
- `created_at`

**服务方法**

- `add_required_certification(workstation_id, data)`
  - 为工位增加资质要求
  - 校验工位和证书主数据存在


### 7.6 WorkstationEquipmentRequirement / 工位设备授权要求

**代码位置**

- Model: `app/models/shopfloor_structure.py`
- Service: `app/services/shopfloor_structure.py`

**建模职责**

表达员工在某工位作业时，需要具备哪些设备代码及授权等级。

**关键字段**

- `id`
- `workstation_id`
- `equipment_code`
- `required_authorization_level`
- `created_at`

**服务方法**

- `add_equipment_requirement(workstation_id, data)`
  - 增加工位设备授权要求
  - 校验授权等级合法


### 7.7 EmployeeTeamAssignment / 员工班组归属

**代码位置**

- Model: `app/models/shopfloor_worker_profile.py`
- Service: `app/services/shopfloor_worker_profile.py`

**建模职责**

记录员工在某时间段内属于哪个班组、哪条产线，以及是否是主要归属。

**关键字段**

- `id`
- `employee_id`
- `team_id`
- `line_id`
- `start_date`
- `end_date`
- `is_primary`
- `created_at`

**服务方法**

- `create_team_assignment(data)`
  - 创建班组归属记录
  - 校验员工、班组、产线存在
  - 校验结束日期不早于开始日期

**业务定位**

该实体是“人员组织归属历史”表，可支撑跨线支援、主归属判定和历史追溯。


### 7.8 EmployeeProductionProfile / 员工生产画像

**代码位置**

- Model: `app/models/shopfloor_worker_profile.py`
- Service: `app/services/shopfloor_worker_profile.py`

**建模职责**

该实体补充员工在制造现场维度下的生产属性，用来表达“这个人是否可参与现场排班与支援”。

**关键字段**

- `id`
- `employee_id`
- `worker_type`
- `production_status`
- `can_support_lines`
- `notes`
- `created_at`
- `updated_at`

**约束**

- `employee_id` 唯一，一个员工只允许一份生产画像
- `can_support_lines` 以 JSON 字符串形式持久化

**枚举约束**

- `worker_type`: `operator / inspector / technician / team_leader`
- `production_status`: `active / inactive / restricted`

**服务方法**

- `create_profile(data)`
  - 创建生产画像
  - 防止同员工重复建档
  - 序列化 `can_support_lines`
- `get_profile(employee_id)`
  - 按员工查询生产画像
- `update_profile(employee_id, data)`
  - 更新画像
  - 校验类型和状态枚举

**业务定位**

这是排班资格的前置门槛。若员工生产画像不存在或状态不是 `active`，工位资格校验会直接报高风险问题。


## 8. 资格、培训与安全合规

### 8.1 Certification / 证书主数据

**代码位置**

- Model: `app/models/credential.py`
- Service: `app/services/credential.py`

**建模职责**

定义证书/资格的标准模板，是员工证书记录和工位证书要求的来源。

**关键字段**

- `id`
- `name`
- `category`
- `required_training_hours`
- `validity_months`
- `description`
- `created_at`
- `updated_at`

**枚举约束**

- `category`: `safety / equipment / process / quality`

**服务方法**

- `create_certification(data)`
  - 创建证书主数据
- `update_certification(certification_id, data)`
  - 更新证书主数据
  - 校验证书类别


### 8.2 EmployeeCertification / 员工资质

**代码位置**

- Model: `app/models/credential.py`
- Service: `app/services/credential.py`

**建模职责**

记录员工已获得的证书、有效期、状态和佐证信息，是工位资格检查的核心数据之一。

**关键字段**

- `id`
- `employee_id`
- `certification_id`
- `issued_at`
- `expires_at`
- `status`
- `evidence`
- `created_at`
- `updated_at`

**枚举约束**

- `status`: `valid / expired / revoked`

**服务方法**

- `create_employee_certification(data)`
  - 创建员工证书记录
  - 校验员工、证书存在
- `update_employee_certification(record_id, data)`
  - 更新证书记录
- `expiring_certifications(days=30)`
  - 查询即将到期证书


### 8.3 EquipmentAuthorization / 设备授权

**代码位置**

- Model: `app/models/credential.py`
- Service: `app/services/credential.py`

**建模职责**

记录员工针对某设备代码的操作授权级别和有效性，用于高风险工位与设备作业准入判断。

**关键字段**

- `id`
- `employee_id`
- `equipment_code`
- `authorization_level`
- `issued_at`
- `expires_at`
- `status`
- `created_at`
- `updated_at`

**枚举约束**

- `authorization_level`: `observer / operator / maintainer`
- `status`: `valid / expired / revoked`

**服务方法**

- `create_equipment_authorization(data)`
  - 创建设备授权
- `update_equipment_authorization(record_id, data)`
  - 更新授权
- `expiring_authorizations(days=30)`
  - 查询即将到期授权

**辅助规则**

`app/services/credential.py` 中 `LEVEL_RANK` 定义了授权级别的高低，用于工位资格判断时比较权限是否达标。


### 8.4 SafetyTraining / 安全培训

**代码位置**

- Model: `app/models/safety_compliance.py`
- Service: `app/services/safety_compliance.py`

**建模职责**

定义培训课程主数据，描述安全培训类型、有效期以及与证书的关系。

**关键字段**

- `id`
- `title`
- `category`
- `required_for_certification_id`
- `validity_months`
- `description`
- `created_at`
- `updated_at`

**枚举约束**

- `category`: `general / line / equipment / hazard`

**服务方法**

- `create_safety_training(data)`
  - 创建培训定义
  - 若绑定证书，则校验证书存在


### 8.5 EmployeeSafetyRecord / 员工安全记录

**代码位置**

- Model: `app/models/safety_compliance.py`
- Service: `app/services/safety_compliance.py`

**建模职责**

记录员工完成某培训的时间、成绩、有效期和状态，用于高风险工位的安全准入判断。

**关键字段**

- `id`
- `employee_id`
- `training_id`
- `completed_at`
- `score`
- `expires_at`
- `status`
- `created_at`

**枚举约束**

- `status`: `valid / expired / failed`

**服务方法**

- `create_safety_record(data)`
  - 创建员工安全培训记录
- `safety_status(employee_id)`
  - 汇总员工是否存在有效安全培训
  - 返回完整培训记录
- `expiring_safety_records(days=30)`
  - 查询即将到期的安全记录

**业务定位**

这张表在高风险工位场景中直接参与准入判断，是安全合规的强约束实体。


## 9. 工单、排班与现场执行

### 9.1 ProductionOrder / 生产工单

**代码位置**

- Model: `app/models/work_order.py`
- Service: `app/services/work_order.py`

**建模职责**

生产工单描述要生产什么、在哪条线生产、计划时间和优先级，是排班和风险分析的上游业务对象。

**关键字段**

- `id`
- `order_no`
- `product_name`
- `line_id`
- `planned_quantity`
- `planned_start_date`
- `planned_end_date`
- `status`
- `priority`
- `description`
- `created_at`
- `updated_at`

**约束**

- `order_no` 唯一

**枚举约束**

- `status`: `planned / running / paused / completed / cancelled`
- `priority`: `low / normal / high / urgent`

**服务方法**

- `create_order(data)`
  - 创建工单
  - 校验产线、状态、优先级
- `update_order(order_id, data)`
  - 更新工单
  - 支持重新挂接产线
- `staffing_context(order_id)`
  - 返回工单及其全部工序
  - 供人员排班和分析使用


### 9.2 ProductionOrderOperation / 工单工序

**代码位置**

- Model: `app/models/work_order.py`
- Service: `app/services/work_order.py`

**建模职责**

工序记录把工单拆解到具体工位、顺序和人力需求层，是工单与工位、排班之间的桥梁。

**关键字段**

- `id`
- `order_id`
- `workstation_id`
- `process_code`
- `sequence`
- `planned_hours`
- `required_headcount`
- `status`
- `created_at`
- `updated_at`

**枚举约束**

- `status`: `planned / running / completed`

**服务方法**

- `create_operation(order_id, data)`
  - 为工单增加工序
  - 校验工单与工位存在


### 9.3 ShiftDefinition / 班次定义

**代码位置**

- Model: `app/models/shift_staffing.py`
- Service: `app/services/shift_staffing.py`

**建模职责**

班次定义抽象了白班、夜班、加班班次的时间和津贴规则，是排班计划模板。

**关键字段**

- `id`
- `code`
- `name`
- `start_time`
- `end_time`
- `shift_type`
- `allowance_rate`
- `created_at`
- `updated_at`

**约束**

- `code` 唯一

**枚举约束**

- `shift_type`: `day / night / overtime`

**服务方法**

- `create_shift(data)`
  - 创建班次定义
- `update_shift(shift_id, data)`
  - 更新班次定义


### 9.4 ProductionShiftPlan / 排班计划

**代码位置**

- Model: `app/models/shift_staffing.py`
- Service: `app/services/shift_staffing.py`

**建模职责**

排班计划定义某条产线在某日期某班次需要多少人，以及当前计划状态，是现场人力调度的主对象。

**关键字段**

- `id`
- `order_id`
- `line_id`
- `shift_id`
- `work_date`
- `required_headcount`
- `status`
- `created_by`
- `created_at`
- `updated_at`

**约束**

- `(line_id, work_date, shift_id)` 复合索引

**枚举约束**

- `status`: `draft / published / adjusted / closed`

**服务方法**

- `create_shift_plan(data)`
  - 创建排班计划
  - 校验产线、班次、关联工单、状态值
- `validate_shift_plan(plan_id)`
  - 对计划进行规则校验
  - 检查缺员、请假冲突、同日多班冲突、工位资格不满足等问题
- `publish_shift_plan(plan_id)`
  - 发布排班计划
  - 若存在风险则自动生成风险信号并拒绝发布

**业务定位**

这是制造域最重要的调度实体之一，串联员工、工位、请假、技能、资质、安全和风险。


### 9.5 EmployeeShiftAssignment / 员工排班分配

**代码位置**

- Model: `app/models/shift_staffing.py`
- Service: `app/services/shift_staffing.py`

**建模职责**

员工排班分配表示某员工被安排到某排班计划中的具体工位。

**关键字段**

- `id`
- `plan_id`
- `employee_id`
- `workstation_id`
- `assignment_type`
- `status`
- `created_at`
- `updated_at`

**枚举约束**

- `assignment_type`: `normal / support / overtime / replacement`
- `status`: `planned / confirmed / cancelled`

**服务方法**

- `create_assignment(data)`
  - 创建员工排班分配
  - 校验排班计划、员工、工位和枚举值

**业务定位**

这是排班计划下的执行层实体，也是排班校验、冲突检测和风险追踪的直接对象。


### 9.6 工位资格校验能力

虽然不是单独实体，但它是多个实体共同作用的核心能力，主要由 `app/services/shift_staffing.py` 提供：

- `_has_valid_certification(...)`
- `_has_required_authorization(...)`
- `_has_skill(...)`
- `_has_valid_safety(...)`
- `check_workstation_eligibility(employee_id, workstation_id, ...)`

该能力会联合使用以下实体：

- `EmployeeProductionProfile`
- `EmployeeSkill`
- `EmployeeCertification`
- `EquipmentAuthorization`
- `EmployeeSafetyRecord`
- `WorkstationRequiredSkill`
- `WorkstationRequiredCertification`
- `WorkstationEquipmentRequirement`

输出结果为 `ValidationResult`，其中包含多个 `ValidationIssue`。这也是风险信号生成的直接来源。


## 10. 风险治理

### 10.1 ProductionRiskSignal / 风险信号

**代码位置**

- Model: `app/models/operational_risk.py`
- Service: `app/services/operational_risk.py`

**建模职责**

风险信号记录现场调度、资质、安全、排班冲突等问题，是系统自动风控与人工复核之间的衔接层。

**关键字段**

- `id`
- `order_id`
- `employee_id`
- `line_id`
- `workstation_id`
- `shift_assignment_id`
- `signal_type`
- `severity`
- `evidence`
- `status`
- `detected_by`
- `created_at`
- `updated_at`

**枚举约束**

- `severity`: `low / medium / high / critical`
- `status`: `open / reviewed / resolved / ignored`
- `detected_by`: `human / system / agent`

**服务方法**

- `create_risk_signal(data)`
  - 手工创建风险信号
  - `evidence` 以 JSON 字符串存储
- `update_risk_signal(risk_id, data)`
  - 更新风险信号
  - 支持更新证据内容
- `generate_shift_plan_risks(plan_id)`
  - 基于排班校验结果批量生成风险信号
  - 风险证据中自动附带 `plan_id` 和消息说明

**业务定位**

这是制造风控的事实表，也是后续 Agent 审核、风险看板和人工复核工作流的基础。


### 10.2 ProductionRiskReview / 风险复核

**代码位置**

- Model: `app/models/operational_risk.py`
- Service: `app/services/operational_risk.py`

**建模职责**

风险复核记录人工或 Agent 对某条风险信号的审查意见和处理建议。

**关键字段**

- `id`
- `risk_signal_id`
- `reviewer`
- `conclusion`
- `action_suggestion`
- `created_at`

**服务方法**

- `create_risk_review(risk_id, data)`
  - 创建风险复核记录
  - 同时把对应风险信号状态更新为 `reviewed`

**业务定位**

这张表代表风险闭环中的“处理意见层”，把检测结果与决策动作区分开来。


## 11. 项目协同实体

### 11.1 Project / 项目

**代码位置**

- Model: `app/models/project.py`
- Service: `app/services/project.py`

**建模职责**

项目实体用于承接改善项目、专项任务或跨部门协同工作，不直接等同于制造工单，但可用于产线改进、专项支持、临时项目化工作。

**关键字段**

- `id`
- `name`
- `description`
- `status`
- `start_date`
- `end_date`
- `created_at`

**枚举约束**

- `status`: `planning / active / completed`

**服务方法**

- `list_projects(status=None)`
- `get_project(project_id)`
- `create_project(project_in)`
  - 校验状态与日期范围
- `update_project(project_id, project_in)`
  - 校验状态与日期范围
- `delete_project(project_id)`
  - 活跃项目禁止删除
- `get_project_progress(project_id)`
  - 汇总预算人天、已用人天、按需求和按成员的进度


### 11.2 ProjectSkillRequirement / 项目技能需求

**建模职责**

定义项目需要什么技能、需要多少人、需要多少预算人天。

**关键字段**

- `id`
- `project_id`
- `skill_id`
- `required_proficiency`
- `person_days`
- `headcount`
- `created_at`

**约束**

- `project_id + skill_id` 唯一

**服务方法**

- `list_skill_requirements(project_id)`
- `create_skill_requirement(project_id, req_in)`
  - 校验项目、技能、熟练度、预算人天、人头数
- `update_skill_requirement(project_id, req_id, req_in)`
- `delete_skill_requirement(project_id, req_id)`


### 11.3 ProjectMember / 项目成员

**建模职责**

记录员工参与某项目的角色和加入时间。

**关键字段**

- `id`
- `project_id`
- `employee_id`
- `role`
- `assigned_date`
- `created_at`

**约束**

- `project_id + employee_id` 唯一

**服务方法**

- `list_members(project_id)`
- `create_member(project_id, member_in)`
  - 校验项目存在、员工存在、员工未重复加入
- `update_member(project_id, member_id, member_in)`
- `delete_member(project_id, member_id)`


### 11.4 ProjectTimesheet / 项目工时

**建模职责**

记录员工在项目某技能需求上的工时投入，是项目进度和成员工作量分析的依据。

**关键字段**

- `id`
- `project_id`
- `requirement_id`
- `employee_id`
- `date`
- `hours`
- `description`
- `created_at`

**服务方法**

- `list_timesheets(project_id, employee_id=None, requirement_id=None)`
- `create_timesheet(project_id, ts_in)`
  - 校验项目、需求、成员归属、工时值和日期
- `update_timesheet(project_id, timesheet_id, ts_in)`
- `delete_timesheet(project_id, timesheet_id)`

**业务定位**

这组实体和制造主流程不是完全同一条线，但非常适合承载改善项目、专项排障和跨线支援统计。


## 12. Agent 记忆实体

### 12.1 AgentMemory / Agent 记忆

**代码位置**

- Model: `app/models/agent_memory.py`
- Service: `app/services/agent_memory.py`

**建模职责**

持久化用户偏好、长期事实、提醒事项等上下文信息，为智能代理提供会话外记忆能力。

**关键字段**

- `id`
- `session_id`
- `user_tag`
- `memory_type`
- `category`
- `subject`
- `content`
- `source`
- `importance`
- `expires_at`
- `is_active`
- `created_at`
- `updated_at`

**服务方法**

- `save_memory(memory_in)`
  - 保存记忆
  - 若是同一用户的 `preference` 且主题相同，则更新而不是新增
- `recall_memories(user_tag, memory_type=None, category=None, subject=None, keyword=None, limit=20)`
  - 召回记忆
  - 支持按主题、关键字、类别过滤
- `get_memory(memory_id)`
- `update_memory(memory_id, memory_in)`
- `delete_memory(memory_id)`
- `cleanup_expired()`
  - 失效过期记忆


### 12.2 MemoryReminder / 记忆提醒

**建模职责**

为某条记忆配置提醒时间与提醒类型，实现记忆的主动触发。

**关键字段**

- `id`
- `memory_id`
- `reminder_type`
- `trigger_at`
- `recurrence_rule`
- `triggered`
- `trigger_count`
- `created_at`

**服务方法**

- `create_reminder(memory_id, reminder_in)`
  - 为记忆创建提醒
- `check_pending_reminders(user_tag)`
  - 查询并标记已触发提醒
- `dismiss_reminder(reminder_id)`
  - 删除提醒


### 12.3 ConversationMessage / 会话消息

**建模职责**

保存智能代理会话消息、工具调用信息和推理内容，支撑会话追溯。

**关键字段**

- `id`
- `session_id`
- `user_tag`
- `role`
- `content`
- `tool_call_id`
- `tool_calls`
- `reasoning_content`
- `created_at`

**服务方法**

- `get_session_messages(session_id)`
  - 查询某会话全部消息

**业务定位**

这是 Agent 交互审计与上下文追踪的基础实体。


## 13. 知识库能力说明

`knowledge_base` 当前不是典型关系型实体建模，而是向量知识能力模块，主要提供：

- `add_document_from_text(...)`
- `add_document_from_file(...)`
- `search_documents(...)`
- `list_documents()`
- `delete_document(doc_id)`

它不属于本文重点的数据库实体表，但在业务能力上会与以下实体联动：

- 工位资格判断
- 安全培训与 SOP 查询
- 排班风险解释
- 项目与现场知识检索


## 14. 当前实体能力映射总结

### 14.1 主数据层

- `Department`: 组织归属与删除前员工约束
- `Employee`: 人员主档
- `SkillCatalog`: 技能标准主数据
- `EmployeeSkill`: 人员能力事实表

### 14.2 人力协同层

- `Attendance`: 出勤与工时
- `Leave`: 休假申请与审批
- `Payroll`: 月度薪资核算
- `Project*`: 项目、成员、技能需求、工时

### 14.3 生产现场层

- `ProductionLine`: 产线主档
- `ProductionTeam`: 班组主档
- `Workstation`: 工位主档
- `EmployeeTeamAssignment`: 现场归属历史
- `EmployeeProductionProfile`: 现场画像
- `ProductionOrder*`: 工单与工序
- `ShiftDefinition`: 班次模板
- `ProductionShiftPlan`: 排班主表
- `EmployeeShiftAssignment`: 排班明细

### 14.4 合规与风险层

- `Certification`: 证书标准
- `EmployeeCertification`: 员工资格
- `EquipmentAuthorization`: 设备授权
- `SafetyTraining`: 培训标准
- `EmployeeSafetyRecord`: 培训结果
- `ProductionRiskSignal`: 风险事实
- `ProductionRiskReview`: 风险复核

### 14.5 Agent 增强层

- `AgentMemory`: 长短期记忆
- `MemoryReminder`: 主动提醒
- `ConversationMessage`: 会话记录


## 15. 关键业务闭环

### 15.1 员工上岗资格闭环

涉及实体：

- `Employee`
- `EmployeeProductionProfile`
- `EmployeeSkill`
- `EmployeeCertification`
- `EquipmentAuthorization`
- `EmployeeSafetyRecord`
- `Workstation*Requirement`

核心方法：

- `check_workstation_eligibility(...)`

### 15.2 排班发布闭环

涉及实体：

- `ProductionShiftPlan`
- `EmployeeShiftAssignment`
- `Leave`
- `EmployeeProductionProfile`
- `EmployeeSkill`
- `EmployeeCertification`
- `EquipmentAuthorization`
- `EmployeeSafetyRecord`
- `ProductionRiskSignal`

核心方法：

- `validate_shift_plan(plan_id)`
- `publish_shift_plan(plan_id)`
- `generate_shift_plan_risks(plan_id)`

### 15.3 薪资计算闭环

涉及实体：

- `Employee`
- `Attendance`
- `Leave`
- `Payroll`

核心方法：

- `generate_monthly_payroll(month)`
- `get_payslip(payroll_id)`


## 16. 后续建模优化建议

### 16.1 增强外键与关系表达

当前代码大量依赖 Service 层手工校验。若后续数据量增大，建议逐步补齐：

- 数据库外键
- ORM relationship
- 删除级联策略

### 16.2 统一领域命名

建议逐步完成从旧 HR 命名到制造领域命名的统一，例如：

- `Employee` -> `Worker`
- `Department` -> `OrgUnit`
- `SkillCatalog` -> `SkillDefinition`

但兼容层需要保留一段时间，以免影响现有 API 和测试。

### 16.3 补充通用查询方法

当前部分 shopfloor 实体以创建、更新和单查为主，后续建议补充：

- 班组列表查询
- 工位列表查询
- 员工资格视图
- 工单工序查询
- 风险闭环查询

### 16.4 补充状态机定义

以下实体已具备明显状态流，建议后续显式沉淀状态机：

- `Leave`
- `Payroll`
- `ProductionOrder`
- `ProductionShiftPlan`
- `EmployeeShiftAssignment`
- `ProductionRiskSignal`


## 17. 总结

当前项目已经具备一套比较清晰的制造人员运营建模骨架：

- 基础主档由 `Department + Employee + SkillCatalog` 构成
- 现场结构由 `ProductionLine + ProductionTeam + Workstation` 构成
- 人员资格由技能、证书、授权、安全记录共同决定
- 调度中心由工单、排班计划、排班分配和风险信号串联
- 协同支持由考勤、请假、薪资、项目承接
- 智能增强由知识库和 Agent 记忆提供

从设计上看，这个项目的重点已经不是传统 HR 信息维护，而是“制造现场的人岗匹配、排班合规和风险治理”。后续无论是扩展 API、报表还是 Agent Skill，建议都沿着这条主线继续演进。
