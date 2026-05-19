# 业务领域模块说明

本文档仅描述 `app/models`、`app/repositories`、`app/services`、`app/routers` 中的业务领域模块实现能力，不包含 `app/agent` 运行时能力，也不包含 `frontend` 前端部分。

## 1. 总体说明

当前后端业务实现按领域拆分为九个模块：

1. `organization` 组织
2. `workforce` 人员
3. `capability` 能力
4. `qualification` 资质
5. `shopfloor` 车间现场
6. `production` 生产
7. `staffing` 排班
8. `attendance` 考勤与薪资
9. `risk` 风险

每个领域基本遵循相同实现结构：

- `models`：定义 ORM 业务实体与实体关系字段
- `repositories`：负责数据库读写
- `services`：负责业务校验、唯一性检查和跨模块引用校验
- `routers`：提供 REST API 接口

从 `main.py` 可见，上述九个业务模块都已注册到 FastAPI 应用中，属于当前系统正式对外提供的后端业务能力。

## 2. 模块关系概览

系统围绕“员工”和“制造现场对象”两条主线组织业务：

- `organization` 维护组织单元层级与负责人
- `workforce` 维护员工主档以及员工在组织、产线、班组中的任职分配
- `capability` 维护技能目录与员工技能画像
- `qualification` 维护证书、安全培训、员工培训记录和设备授权
- `shopfloor` 维护产线、班组、工位等现场对象
- `production` 维护生产订单与生产工序
- `staffing` 维护班次模板、排班计划与排班分配
- `attendance` 维护考勤、请假和薪资记录
- `risk` 维护现场风险信号与风险复核记录

关键业务联动体现在：

- 员工会关联组织、技能、证书、培训、设备授权、排班、考勤、请假、薪资和风险
- 工位会关联产线、工序、排班分配和风险信号
- 产线会关联班组、工位、生产订单、排班计划和风险信号
- 排班会把生产任务、班次模板、员工和工位落到具体工作日
- 风险信号可以挂接到订单、员工、产线、工位和排班分配

## 3. 各业务领域模块说明

### 3.1 `organization` 组织模块

#### 模块职责

组织模块用于维护制造现场的组织单元主数据，例如工厂、部门、车间等，并表达父子层级与负责人关系。

#### 核心对象

- `OrganizationUnit`
  - 关键字段：`name`、`code`、`unit_type`、`parent_id`、`manager_worker_id`、`status`
  - 支持组织树结构
  - 支持绑定负责人员工

#### 已实现功能

- 组织单元的新增、查询、更新、删除
- 按 `unit_type`、`status`、`parent_id` 过滤查询组织单元
- 查询某组织单元的下级组织单元
- 查询某位员工负责的组织单元

#### 关键业务规则

- 组织单元 `code` 唯一
- 组织单元 `name` 唯一
- `parent_id` 如填写，必须引用已存在的组织单元
- `manager_worker_id` 如填写，必须引用已存在的员工

### 3.2 `workforce` 人员模块

#### 模块职责

人员模块负责维护员工主档，以及员工在组织、产线、班组中的任职与归属记录，是其他模块的人力主索引。

#### 核心对象

- `Worker`
  - 关键字段：`worker_code`、`full_name`、`employment_type`、`status`、`organization_unit_id`
  - 同时包含入离职日期、基础工资、联系方式、备注等信息
- `WorkerAssignment`
  - 关键字段：`worker_id`、`organization_unit_id`、`production_line_id`、`production_team_id`
  - 还包含 `role_title`、`assignment_type`、`status`、`start_date`、`end_date`、`is_primary`
  - 用于表示员工在现场体系中的任职关系

#### 已实现功能

- 员工主档的新增、查询、更新、删除
- 按组织、用工类型、状态筛选员工
- 任职分配记录的新增、查询、更新、删除
- 按员工、组织单元、产线、班组查询任职记录
- 查询某员工在某工作日维度下可追溯的归属信息基础数据

#### 关键业务规则

- 员工 `worker_code` 唯一
- 员工如绑定组织单元，组织单元必须存在
- 任职记录引用的员工、组织、产线、班组必须存在
- 任职记录 `start_date` 不能晚于 `end_date`
- 同一员工下，相同组织/产线/班组/角色/任职类型/开始日期的任职记录不能重复

### 3.3 `capability` 能力模块

#### 模块职责

能力模块用于维护技能目录，以及员工具备的技能记录，为能力盘点和后续资格判断提供基础数据。

#### 核心对象

- `Skill`
  - 关键字段：`name`、`code`、`category`、`status`
  - 表示标准技能目录
- `WorkerSkill`
  - 关键字段：`worker_id`、`skill_id`、`proficiency_level`
  - 还包含 `years_of_experience`、`validated`、`notes`
  - 表示员工技能掌握情况

#### 已实现功能

- 技能目录的新增、查询、更新、删除
- 按类别、状态过滤技能
- 员工技能记录的新增、查询、更新、删除
- 按员工、技能过滤查询员工技能

#### 关键业务规则

- 技能 `name` 唯一
- 技能 `code` 唯一
- 员工技能记录要求员工和技能均存在
- 同一员工与同一技能只能存在一条技能记录

### 3.4 `qualification` 资质模块

#### 模块职责

资质模块统一管理员工上岗相关的证书、培训和设备授权信息，是“员工是否具备相应资格”的事实来源。

#### 核心对象

- `Certification`
  - 标准证书目录，包含类别、有效期月数、发证机构等定义
- `WorkerCertification`
  - 员工持证记录，包含证书编号、签发时间、到期时间、状态和凭证地址
- `SafetyTraining`
  - 安全培训目录，可关联技能，也可指定前置证书
- `WorkerSafetyTraining`
  - 员工培训完成记录，包含完成时间、到期时间、分数和状态
- `EquipmentAuthorization`
  - 员工设备授权记录，包含设备编码、授权等级、有效期、状态和凭证地址

#### 已实现功能

- 证书目录的新增、查询、更新、删除
- 员工持证记录的新增、查询、更新、删除
- 安全培训目录的新增、查询、更新、删除
- 员工培训完成记录的新增、查询、更新、删除
- 设备授权记录的新增、查询、更新、删除
- 按类别、员工、状态等维度查询资质信息

#### 关键业务规则

- 证书 `name` 唯一，`code` 唯一
- 安全培训 `code` 唯一
- 员工证书记录要求员工和证书存在
- 员工证书记录 `issued_at` 不能晚于 `expires_at`
- 同一员工与同一证书只能存在一条记录
- 员工培训记录要求员工和培训目录存在
- 员工培训记录 `completed_at` 不能晚于 `expires_at`
- 同一员工与同一培训只能存在一条记录
- 设备授权记录要求员工存在
- 设备授权记录 `issued_at` 不能晚于 `expires_at`
- 同一员工与同一设备编码只能存在一条记录
- 培训如关联技能或前置证书，被关联对象必须存在

### 3.5 `shopfloor` 车间现场模块

#### 模块职责

车间现场模块用于表达制造现场的结构化对象，包括产线、班组和工位，是订单、排班和风险挂接的现场底座。

#### 核心对象

- `ProductionLine`
  - 关键字段：`organization_unit_id`、`code`、`name`、`supervisor_worker_id`、`status`
- `ProductionTeam`
  - 关键字段：`production_line_id`、`code`、`name`、`leader_worker_id`、`shift_pattern`
- `Workstation`
  - 关键字段：`production_line_id`、`code`、`name`、`workstation_type`、`risk_level`、`status`

#### 已实现功能

- 产线的新增、查询、更新、删除
- 班组的新增、查询、更新、删除
- 工位的新增、查询、更新、删除
- 按组织单元、产线、状态等维度查询现场对象

#### 关键业务规则

- 同一组织单元下，产线 `code` 唯一
- 同一产线下，班组 `code` 唯一
- 同一产线下，工位 `code` 唯一
- 产线负责人、班组负责人如填写，必须引用已存在员工
- 现场对象引用的组织单元或产线必须存在

### 3.6 `production` 生产模块

#### 模块职责

生产模块负责管理生产订单与生产工序，将现场配置与实际生产任务连接起来。

#### 核心对象

- `ProductionOrder`
  - 关键字段：`order_number`、`production_line_id`、`product_code`、`product_name`
  - 还包含计划数量、计划开始结束时间、优先级、状态等字段
- `ProductionOperation`
  - 关键字段：`production_order_id`、`workstation_id`、`operation_code`、`operation_name`
  - 还包含 `sequence_number`、`planned_hours`、`required_headcount`、`status`

#### 已实现功能

- 生产订单的新增、查询、更新、删除
- 按产线、状态过滤生产订单
- 生产工序的新增、查询、更新、删除
- 按订单、工位、状态过滤工序

#### 关键业务规则

- `order_number` 唯一
- 生产订单绑定的产线必须存在
- 生产工序绑定的订单和工位必须存在
- 同一生产订单下 `sequence_number` 不能重复

### 3.7 `staffing` 排班模块

#### 模块职责

排班模块负责把班次规则、某天某条产线的人力计划和最终人员落位串起来，是从计划到执行的核心模块。

#### 核心对象

- `ShiftTemplate`
  - 关键字段：`code`、`name`、`shift_type`、`start_time`、`end_time`、`allowance_rate`
  - 表示班次模板与津贴规则
- `ShiftPlan`
  - 关键字段：`production_line_id`、`shift_template_id`、`work_date`、`required_headcount`
  - 可选关联 `production_order_id`
  - 表示某条产线某天某班次的人力计划
- `ShiftAssignment`
  - 关键字段：`shift_plan_id`、`worker_id`、`workstation_id`
  - 还包含 `assignment_type`、`status`、`assigned_role`
  - 表示最终排班分配结果

#### 已实现功能

- 班次模板的新增、查询、更新、删除
- 排班计划的新增、查询、更新、删除
- 排班分配记录的新增、查询、更新、删除
- 按产线、班次模板、日期、状态过滤排班计划
- 按员工、工位、排班计划、状态过滤排班分配
- 查询某员工在某工作日的排班记录

#### 关键业务规则

- 班次模板 `code` 唯一
- 同一产线、同一工作日、同一班次模板只能存在一条排班计划
- 排班计划引用的产线、班次模板和生产订单如填写必须存在
- 排班分配引用的排班计划、员工、工位必须存在
- 同一 `shift_plan + worker + workstation` 组合不能重复

### 3.8 `attendance` 考勤与薪资模块

#### 模块职责

该模块负责记录员工考勤、请假申请和薪资结果，为后续核算或追溯提供基础数据。

#### 核心对象

- `AttendanceRecord`
  - 关键字段：`worker_id`、`work_date`、`check_in_time`、`check_out_time`、`status`、`work_hours`
- `LeaveRequest`
  - 关键字段：`worker_id`、`leave_type`、`leave_type_name`、`start_date`、`end_date`
  - 还包含 `requested_days`、`reason`、`status`、`approver_name`、`approved_at`
- `PayrollRecord`
  - 关键字段：`worker_id`、`pay_period`、`base_salary`、`bonuses`、`deductions`、`net_salary`
  - 还包含支付状态和支付日期

#### 已实现功能

- 考勤记录的新增、查询、更新、删除
- 请假申请的新增、查询、更新、删除
- 薪资记录的新增、查询、更新、删除
- 按员工、日期、状态、周期等维度查询三类记录

#### 关键业务规则

- 同一员工同一工作日只能存在一条考勤记录
- 考勤记录要求员工存在，且签到时间不能晚于签退时间
- 请假记录要求员工存在，且开始日期不能晚于结束日期
- 同一员工同一薪资期间只能存在一条薪资记录
- 薪资记录要求员工存在

### 3.9 `risk` 风险模块

#### 模块职责

风险模块负责记录制造现场的运营风险信号，并通过复核记录沉淀处理结论。

#### 核心对象

- `OperationalRiskSignal`
  - 关键字段：`signal_type`、`severity`、`status`、`detected_by`、`evidence`
  - 可选关联：`production_order_id`、`worker_id`、`production_line_id`、`workstation_id`、`shift_assignment_id`
- `OperationalRiskReview`
  - 关键字段：`risk_signal_id`、`reviewer_name`、`conclusion`、`action_suggestion`、`review_status`

#### 已实现功能

- 风险信号的新增、查询、更新、删除
- 按订单、员工、产线、工位、排班分配、状态过滤风险信号
- 风险复核记录的新增、查询、更新、删除

#### 关键业务规则

- 风险信号关联的订单、员工、产线、工位、排班分配如填写必须存在
- 风险复核必须关联已存在的风险信号

## 4. 当前业务实现的特点

从代码实现看，当前系统已经不是单纯的基础 CRUD 集合，而是具备以下业务骨架：

- 有完整的组织、人员、技能、资质、产线、班组、工位、订单、排班、考勤、风险对象体系
- 服务层对唯一键、日期有效性和跨实体引用做了显式校验
- 路由层为各领域提供了清晰的 REST API 入口
- 人员、现场、生产、排班和风险之间已经形成可串联的数据链路

同时也要注意，当前实现的重点仍然是“结构化数据维护与校验”，尚未在业务后端中实现复杂排班算法、自动薪资计算、自动资质判定或闭环处置流。

## 5. 不包含的内容

本文档刻意不覆盖以下部分：

- `app/agent/*`：对话式 Agent、技能路由、会话记忆、知识库调用等运行时能力
- `frontend/*`：前端页面、状态管理、组件和交互实现
- `app/knowledge_base/*`：知识库切分、向量化、检索相关实现

如果只看业务领域后端，当前项目的核心实现重心就是上述九个领域模块。
