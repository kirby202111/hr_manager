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

每个领域基本都遵循同一实现结构：

- `models`：定义 ORM 业务实体与实体关系
- `repositories`：负责数据库读写
- `services`：负责业务校验、唯一性控制、跨模块关联校验
- `routers`：提供 REST API 接口

从 `main.py` 看，以上九个业务模块都已注册到 FastAPI 应用中，属于当前系统正式对外提供的后端业务能力。

## 2. 模块关系概览

系统以“人员”和“现场岗位/产线”两条主线组织业务：

- `organization` 定义组织层级与负责人
- `workforce` 管理员工主数据以及员工在组织、产线、班组中的任职归属
- `capability` 管理技能目录与员工技能画像
- `qualification` 管理证书、安训、设备授权
- `shopfloor` 定义产线、班组、工位等生产现场对象
- `production` 管理生产订单与工序
- `staffing` 将班次模板、班次计划和人员排班落到具体日期与工位
- `attendance` 记录出勤、请假和薪资结果
- `risk` 记录现场风险信号及复核处理结果

其中最关键的业务联动有：

- 员工会关联组织、技能、证书、安训、设备授权、排班、考勤、请假、薪资、风险
- 工位会关联技能要求、证书要求、设备授权要求、工序、排班、风险
- 产线会关联班组、工位、生产订单、排班计划、风险
- 风险信号可以挂接到订单、员工、产线、工位、排班记录

## 3. 各业务领域模块说明

### 3.1 `organization` 组织模块

#### 模块职责

组织模块用于维护制造现场的组织单元主数据，例如工厂、部门、车间等，并表达组织层级和负责人关系。

#### 核心对象

- `OrganizationUnit`
  - 关键字段：`name`、`code`、`unit_type`、`parent_id`、`manager_worker_id`、`status`
  - 支持父子层级结构
  - 支持绑定负责人员工

#### 已实现功能

- 组织单元的新增、查询、更新、删除
- 按 `unit_type`、`status`、`parent_id` 过滤查询组织单元
- 查询某组织单元的下级组织单元
- 查询某位员工负责的组织单元
- 维护组织与以下业务对象的关联：
  - 员工
  - 员工任职分配
  - 产线

#### 关键业务规则

- 组织单元 `code` 唯一
- 组织单元 `name` 唯一
- 若指定 `parent_id`，必须引用已存在的组织单元
- 若指定 `manager_worker_id`，必须引用已存在的员工

### 3.2 `workforce` 人员模块

#### 模块职责

人员模块负责维护员工主档，以及员工在组织、产线、班组中的任职归属记录，是整个系统的核心主数据模块之一。

#### 核心对象

- `Worker`
  - 关键字段：`worker_code`、`full_name`、`employment_type`、`status`、`organization_unit_id`
  - 同时承载入职/离职日期、基础工资、联系方式、备注等信息
- `WorkerAssignment`
  - 关键字段：`worker_id`、`organization_unit_id`、`production_line_id`、`production_team_id`
  - 还包含 `role_title`、`assignment_type`、`status`、`start_date`、`end_date`、`is_primary`
  - 用于表示员工在组织和生产现场的任职/挂靠关系

#### 已实现功能

- 员工的新增、查询、更新、删除
- 按员工状态、用工类型、组织等条件筛选员工
- 员工任职分配记录的新增、查询、更新、删除
- 按员工、组织单元、产线、班组查询任职记录
- 查询员工在某个日期范围内或某一归属维度下的分配情况
- 作为多个模块的人力主索引，向能力、资质、排班、考勤、风险等模块提供关联锚点

#### 关键业务规则

- 员工 `worker_code` 唯一
- 员工任职记录要求关联的员工、组织、产线、班组必须存在
- 员工任职记录中 `start_date` 不能晚于 `end_date`
- 同一员工下，相同组织/产线/班组/岗位/任职类型/开始日期的任职记录不能重复

### 3.3 `capability` 能力模块

#### 模块职责

能力模块用于维护技能目录，以及员工实际具备的技能画像，为上岗资格判断、工位要求配置和能力盘点提供基础。

#### 核心对象

- `Skill`
  - 关键字段：`name`、`code`、`category`、`status`
  - 表示标准技能目录
- `WorkerSkill`
  - 关键字段：`worker_id`、`skill_id`、`proficiency_level`
  - 还包含 `years_of_experience`、`validated`、`notes`
  - 表示员工拥有哪些技能、熟练度如何、是否经过验证

#### 已实现功能

- 技能目录的新增、查询、更新、删除
- 按技能类别、状态查询技能
- 员工技能记录的新增、查询、更新、删除
- 按员工、技能查询技能画像
- 为以下领域提供能力依赖：
  - 安全培训可关联技能
  - 工位技能要求可引用技能

#### 关键业务规则

- 技能 `name` 唯一
- 技能 `code` 唯一
- 同一员工与同一技能只能建立一条技能记录

### 3.4 `qualification` 资质模块

#### 模块职责

资质模块负责统一管理员工上岗资格相关信息，包括证书、培训、设备授权，是“人是否具备相关资质”的核心事实来源。

#### 核心对象

- `Certification`
  - 标准证书目录，包含证书类别、有效期月数、发证机构等
- `WorkerCertification`
  - 员工持证记录，包含证书编号、签发日期、到期日期、状态、证明材料
- `SafetyTraining`
  - 安全培训目录，可关联技能，也可指定前置证书
- `WorkerSafetyTraining`
  - 员工安训完成记录，包含完成日期、到期日期、分数、状态
- `EquipmentAuthorization`
  - 员工设备操作授权，包含设备编码、授权等级、有效期、状态

#### 已实现功能

- 证书目录的新增、查询、更新、删除
- 员工持证记录的新增、查询、更新、删除
- 安全培训目录的新增、查询、更新、删除
- 员工安训完成记录的新增、查询、更新、删除
- 员工设备授权记录的新增、查询、更新、删除
- 以员工为中心沉淀实际持证、培训、授权情况

#### 关键业务规则

- 证书目录 `name` 唯一，`code` 唯一
- 安全培训 `code` 唯一
- 员工证书记录要求员工和证书存在
- 员工证书记录中 `issued_at` 不能晚于 `expires_at`
- 同一员工与同一证书只能存在一条持证记录
- 员工设备授权记录要求员工存在
- 员工设备授权中 `issued_at` 不能晚于 `expires_at`
- 同一员工与同一设备编码只能存在一条授权记录
- 安全培训如果关联技能或前置证书，被关联对象必须存在

#### 模块价值

这个模块已经具备“资格主数据 + 员工资格记录”的完整骨架，能支撑后续做资质校验、缺口分析、培训补齐、风险预警等能力。

### 3.5 `shopfloor` 车间现场模块

#### 模块职责

车间现场模块用于表达制造现场的空间与组织结构，包括产线、班组、工位，是排班、生产工序、风险定位的承载基础。

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
- 建立现场层级关系：
  - 组织单元 -> 产线
  - 产线 -> 班组
  - 产线 -> 工位
- 建立现场对象与其他模块的关联：
  - 产线关联生产订单、排班计划、风险信号、员工任职
  - 工位关联工位资格要求、工序、排班分配、风险信号

#### 关键业务规则

- 同一组织单元下，产线 `code` 唯一
- 同一产线下，班组 `code` 唯一
- 同一产线下，工位 `code` 唯一
- 产线负责人、班组长如果指定，必须能关联到员工
- 工位通过 `risk_level` 显式承载岗位风险等级

### 3.6 `production` 生产模块

#### 模块职责

生产模块负责管理生产订单及其工序信息，把人力和现场配置与实际生产任务连接起来。

#### 核心对象

- `ProductionOrder`
  - 关键字段：`order_number`、`production_line_id`、`product_code`、`product_name`
  - 还包含计划数量、计划起止日期、优先级、状态等
- `ProductionOperation`
  - 关键字段：`production_order_id`、`workstation_id`、`operation_code`、`operation_name`
  - 还包含 `sequence_number`、`planned_hours`、`required_headcount`、`status`

#### 已实现功能

- 生产订单的新增、查询、更新、删除
- 按产线、状态等维度查询生产订单
- 生产工序的新增、查询、更新、删除
- 按订单、工位、状态查询工序
- 将生产订单与产线绑定
- 将工序挂接到具体工位，并定义顺序、工时和需求人数
- 为排班计划与风险模块提供业务上下文

#### 关键业务规则

- `order_number` 唯一
- 同一生产订单下，`sequence_number` 不能重复
- 生产工序必须关联已存在的生产订单和工位

### 3.7 `staffing` 排班模块

#### 模块职责

排班模块负责把班次规则、某日某产线的人力需求和最终人员安排串起来，是“计划到执行”的核心模块。

#### 核心对象

- `ShiftTemplate`
  - 关键字段：`code`、`name`、`shift_type`、`start_time`、`end_time`、`allowance_rate`
  - 表示班次模板与津贴规则
- `ShiftPlan`
  - 关键字段：`production_line_id`、`shift_template_id`、`work_date`、`required_headcount`
  - 可选关联 `production_order_id`
  - 表示某条产线在某天某班次的人力计划
- `ShiftAssignment`
  - 关键字段：`shift_plan_id`、`worker_id`、`workstation_id`
  - 还包含 `assignment_type`、`status`、`assigned_role`
  - 表示最终分派到个人和工位的班次执行记录

#### 已实现功能

- 班次模板的新增、查询、更新、删除
- 排班计划的新增、查询、更新、删除
- 排班分配明细的新增、查询、更新、删除
- 按员工、工位、班次计划、状态过滤排班分配
- 查询某员工在某个工作日的排班记录
- 将排班计划关联到产线、班次模板、生产订单
- 将排班分配落实到员工与工位

#### 关键业务规则

- 班次模板 `code` 唯一
- 同一产线、同一工作日、同一班次模板只能有一条排班计划
- 排班分配要求关联的班次计划、员工、工位必须存在
- 同一 `shift_plan + worker + workstation` 组合不能重复

#### 模块价值

这个模块已经具备“班次标准 -> 日期计划 -> 员工落位”的完整实现，后续可直接承接资格校验、缺员分析、出勤比对等扩展能力。

### 3.8 `attendance` 考勤与薪资模块

#### 模块职责

该模块负责记录员工出勤结果、请假申请与审批结果，以及薪资结算结果，形成从出勤到发薪的基础数据闭环。

#### 核心对象

- `AttendanceRecord`
  - 关键字段：`worker_id`、`work_date`、`check_in_time`、`check_out_time`、`status`、`work_hours`
- `LeaveRequest`
  - 关键字段：`worker_id`、`leave_type`、`leave_type_name`、`start_date`、`end_date`
  - 还包含 `requested_days`、`reason`、`status`、`approver_name`、`approved_at`
- `PayrollRecord`
  - 关键字段：`worker_id`、`pay_period`、`base_salary`、`bonuses`、`deductions`、`net_salary`
  - 还包含发薪状态和支付日期

#### 已实现功能

- 考勤记录的新增、查询、更新、删除
- 请假申请记录的新增、查询、更新、删除
- 薪资记录的新增、查询、更新、删除
- 按员工、日期、状态、期间等维度查询三类记录
- 将考勤、请假、薪资结果统一归档到员工维度

#### 关键业务规则

- 同一员工同一天只能有一条考勤记录
- 请假记录要求员工存在
- 请假起止日期、审批信息等通过服务层进行基本合法性校验
- 同一员工同一薪资期间只能有一条薪资记录
- 薪资记录要求员工存在

### 3.9 `risk` 风险模块

#### 模块职责

风险模块负责记录生产现场的运营风险信号，并通过复核记录沉淀处理结论和动作建议。

#### 核心对象

- `OperationalRiskSignal`
  - 关键字段：`signal_type`、`severity`、`status`、`detected_by`、`evidence`
  - 可选关联：`production_order_id`、`worker_id`、`production_line_id`、`workstation_id`、`shift_assignment_id`
- `OperationalRiskReview`
  - 关键字段：`risk_signal_id`、`reviewer_name`、`conclusion`、`action_suggestion`、`review_status`

#### 已实现功能

- 风险信号的新增、查询、更新、删除
- 按订单、员工、产线、工位、排班分配、状态查询风险信号
- 风险复核记录的新增、查询、更新、删除
- 将风险与生产、人员、现场、排班上下文关联起来
- 沉淀风险结论和处置建议

#### 关键业务规则

- 风险信号所关联的订单、员工、产线、工位、排班记录如果填写，必须存在
- 风险复核必须关联已存在的风险信号
- 风险信号建立了按状态、创建时间、产线、工位的索引，便于现场检索与跟踪

## 4. 当前业务实现的特点

从代码实现看，当前系统已经不是简单的“基础 CRUD 集合”，而是具备以下业务骨架：

- 有完整的人、岗、线、班、工位、订单、资格、风险对象体系
- 已通过服务层做了大量基础业务校验
- 已显式处理多模块间的关联存在性校验
- 已对重复记录、时间合法性、关键编码唯一性做约束
- 已能支撑制造现场常见的人力运营主线：
  - 员工建档
  - 组织归属
  - 技能与资格维护
  - 工位要求定义
  - 订单与工序配置
  - 排班计划与排班落位
  - 考勤/请假/薪资记录
  - 风险上报与复核

## 5. 不包含的内容

本文档刻意不覆盖以下部分：

- `app/agent/*`：对话式 Agent、技能路由、会话记忆、知识库调用等运行时能力
- `frontend/*`：前端页面、状态管理、组件和交互实现
- `app/knowledge_base/*`：知识库向量检索相关实现

如果只看业务领域后端，本项目的核心实现重心就是以上九个领域模块。
