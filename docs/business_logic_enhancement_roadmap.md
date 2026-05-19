# 业务逻辑增强建议与路线图

本文基于当前产品定位与现有业务模块能力，对 Workforce Ops 在制造现场人力运营场景下仍值得补强的业务逻辑进行整理，并给出一版可落地的增强路线图。

相关参考：

- `README.md` 中的产品目标、核心能力与九大业务领域
- `docs/business_domain_modules.md` 中的现有模块职责、对象关系与已实现规则

## 1. 当前系统能力判断

现有系统已经具备较完整的制造现场业务对象体系，覆盖：

- 组织、员工、任职关系
- 技能、证书、培训、设备授权
- 产线、班组、工位
- 生产订单、生产工序
- 班次模板、排班计划、排班分配
- 考勤、请假、薪资记录
- 风险信号与风险复核

当前实现的明显特点是：

- 主数据结构完整
- 跨模块引用关系较清晰
- 服务层已具备基础业务校验能力
- 已形成从员工到现场、从订单到排班、从排班到风险的可串联数据链路

但当前系统的重心仍偏向“结构化数据维护与校验”，尚未形成足够强的“运营决策规则”和“异常闭环处理能力”。因此，后续优化应优先补足以下几类能力：

- 从“能记录”提升到“能判定”
- 从“能配置”提升到“能约束”
- 从“能查询”提升到“能预警”
- 从“能留痕”提升到“能闭环”

## 2. 优先级建议

以下建议按优先级从高到低排序。

### P0-1. 上岗资格自动判定

#### 建议内容

在排班分配、调班、替岗、跨线支援等关键动作发生前，系统自动判定员工是否满足目标工位或工序的上岗资格要求。

#### 核心判定维度

- 员工状态是否有效
- 是否具备目标技能及最低熟练度
- 证书是否齐全且在有效期内
- 安全培训是否完成且在有效期内
- 设备授权是否满足要求
- 是否存在岗位前置条件未满足的情况

#### 输出结果建议

- `eligible`：允许分配
- `warning`：允许分配但需提示风险
- `blocked`：禁止分配

并输出不满足原因明细，例如：

- 缺少叉车操作证
- 安全培训已过期
- 设备授权等级不足
- 技能熟练度低于工位要求

#### 业务价值

- 直接打通 `capability`、`qualification`、`shopfloor`、`production`、`staffing`
- 让排班从人工经验判断升级为系统约束
- 为自动排班建议、风险触发、复训管理提供基础

---

### P0-2. 排班可用性与冲突校验

#### 建议内容

在 `ShiftAssignment` 新增、更新、调岗时，补充更严格的员工可用性规则。

#### 核心规则建议

- 同一员工同一时间段不可重复排班
- 请假中的员工不可排班
- 已停用、已离职员工不可排班
- 不满足最小休息间隔的员工不可继续排班
- 连续夜班、连续工作天数、单日工时超过阈值时触发预警或拦截
- 跨组织、跨产线、跨班组支援需显式标记

#### 业务价值

- 防止排班数据形式正确但业务上不可执行
- 为考勤核对、薪资核算和风险识别提供干净输入

---

### P0-3. 缺编、错配与关键岗位空岗预警

#### 建议内容

围绕 `ShiftPlan.required_headcount`、`ProductionOperation.required_headcount` 和 `ShiftAssignment` 建立排班达成度分析。

#### 核心预警建议

- 计划人数不足
- 工序需求人数不足
- 关键工位无人覆盖
- 有人但无资格覆盖
- 关键岗位只有单人可替代

#### 业务价值

- 帮助班组长和现场主管快速发现执行风险
- 让系统具备从“事后查询”到“事前预警”的能力

---

### P0-4. 资质到期与复训闭环

#### 建议内容

围绕证书、培训、设备授权建立到期预警和复训补齐闭环。

#### 核心逻辑建议

- 到期前 N 天自动预警
- 到期后自动影响上岗资格结果
- 自动识别受影响的排班、工位、订单和人员
- 自动生成复训、补证、替补安排等待处理事项

#### 业务价值

- 提前暴露资质风险，避免到期后才发现无法排班
- 让 `qualification` 模块从静态台账升级为动态运营模块

---

### P1-1. 排班、考勤、请假的自动对账

#### 建议内容

建立 `ShiftAssignment`、`AttendanceRecord`、`LeaveRequest` 三方对账规则，用于识别执行偏差。

#### 典型异常

- 已排班但无出勤
- 未排班但有出勤
- 已请假但仍排班
- 已请假但仍出勤
- 排班工位与实际出勤记录不一致

#### 业务价值

- 提升现场执行透明度
- 为薪资计算、异常追责和风险识别提供可信基础

---

### P1-2. 风险信号自动触发

#### 建议内容

在 `risk` 模块中补充规则驱动的自动风险识别，不仅允许人工录入，也允许系统基于业务数据自动生成风险信号。

#### 推荐首批自动触发规则

- 无资格上岗
- 证书过期仍排班
- 缺编开线
- 关键工位空岗
- 连续超工时
- 排班与出勤偏差过大

#### 业务价值

- 让风险模块从“记录结果”升级为“持续监控”
- 形成对现场运营的主动管理能力

---

### P1-3. 调班、替岗、支援流程化

#### 建议内容

补充排班执行中的变更过程管理，而不仅保留变更后的最终结果。

#### 建议覆盖的过程

- 调班申请
- 替岗确认
- 跨线支援申请
- 审批或确认留痕
- 调整后的资格重校验

#### 业务价值

- 更贴近制造现场真实执行过程
- 提升数据追溯性与责任可审计性

---

### P2-1. 面向订单的人力匹配与排班建议

#### 建议内容

基于订单工序、工位需求、班次计划和员工能力画像，生成候选员工池和建议排班方案。

#### 建议输出

- 可上岗员工池
- 缺口人数
- 推荐排班名单
- 替补建议
- 需补训人员建议

#### 业务价值

- 将系统从“运营记录工具”提升为“排班决策辅助工具”

---

### P2-2. 自动薪资计算

#### 建议内容

在确保排班与考勤可信后，基于班次、出勤、请假、津贴、扣款和用工类型输出薪资草案。

#### 业务价值

- 减少人工核算工作量
- 提高薪资口径一致性与可追溯性

## 3. 业务逻辑增强路线图

以下路线图按“模块改动点、数据模型补充、接口建议、实施阶段”展开。

---

## 4. 路线图一：上岗资格自动判定

### 模块改动点

- `qualification`
  - 增加资格有效性聚合判断
  - 增加证书、培训、授权的到期状态判断
- `capability`
  - 增加技能等级与工位要求的匹配能力
- `shopfloor`
  - 为工位补充岗位要求定义
- `production`
  - 为工序补充可选资格要求
- `staffing`
  - 在排班分配前接入资格校验

### 数据模型补充

建议新增或补充以下对象/字段：

- `WorkstationRequirement`
  - `workstation_id`
  - `required_skill_id`
  - `min_proficiency_level`
  - `required_certification_id`
  - `required_training_id`
  - `required_authorization_code`
  - `is_mandatory`

- `ProductionOperationRequirement`
  - `production_operation_id`
  - `requirement_type`
  - `reference_id`
  - `min_level`

- `WorkerEligibilitySnapshot`
  - `worker_id`
  - `target_type` (`workstation` / `operation`)
  - `target_id`
  - `status`
  - `checked_at`
  - `reason_codes`
  - `reason_details`

### 接口建议

- `GET /staffing/eligibility/check`
  - 输入：`worker_id`, `workstation_id` 或 `operation_id`, `work_date`
  - 输出：资格判定结果与原因

- `POST /staffing/shift-assignments/validate`
  - 输入：排班分配草案
  - 输出：是否可提交及风险说明

- `GET /qualification/workers/{worker_id}/eligibility`
  - 输出：员工当前可上岗范围

### 实施阶段

#### 第一阶段

- 为工位定义最低资格要求
- 在新增 `ShiftAssignment` 时同步校验
- 返回结构化失败原因

#### 第二阶段

- 引入工序级要求
- 支持批量资格校验
- 增加资格快照缓存

#### 第三阶段

- 与调班、替岗、自动排班建议联动
- 与风险模块联动自动生成风险信号

---

## 5. 路线图二：排班可用性与冲突校验

### 模块改动点

- `staffing`
  - 增加员工可用性判断服务
  - 增加时段冲突检测
- `attendance`
  - 对接请假状态
- `workforce`
  - 对接员工在职状态

### 数据模型补充

- 在 `ShiftTemplate` 补充：
  - `cross_day`
  - `min_rest_hours`
  - `max_continuous_days`
  - `night_shift_flag`

- 在 `ShiftAssignment` 补充：
  - `source_type`（正常排班 / 支援 / 替岗）
  - `conflict_status`
  - `validation_status`
  - `validation_message`

- 可新增 `WorkerAvailabilityRule`
  - `employment_type`
  - `max_daily_hours`
  - `max_weekly_hours`
  - `min_rest_hours`
  - `max_night_shift_streak`

### 接口建议

- `GET /staffing/workers/{worker_id}/availability`
  - 输入：日期范围
  - 输出：可排班窗口、冲突明细、不可排原因

- `POST /staffing/shift-assignments/check-conflicts`
  - 输入：排班分配草案
  - 输出：冲突列表

### 实施阶段

#### 第一阶段

- 实现同时间重复排班检查
- 实现请假冲突检查
- 实现离职/停用检查

#### 第二阶段

- 引入最小休息间隔
- 引入连续工时与夜班规则

#### 第三阶段

- 按员工类型配置不同规则
- 支持批量排班校验

---

## 6. 路线图三：缺编、错配与关键岗位空岗预警

### 模块改动点

- `staffing`
  - 增加排班达成度计算
- `production`
  - 对接工序需求人数
- `shopfloor`
  - 标识关键工位
- `risk`
  - 接收预警结果并生成风险信号

### 数据模型补充

- 在 `Workstation` 补充：
  - `is_critical`
  - `required_headcount`

- 可新增 `StaffingGapAlert`
  - `alert_type`
  - `production_line_id`
  - `shift_plan_id`
  - `workstation_id`
  - `severity`
  - `expected_headcount`
  - `actual_headcount`
  - `qualified_headcount`
  - `status`

### 接口建议

- `GET /staffing/shift-plans/{id}/coverage`
  - 输出：计划人数、已排人数、合格人数、缺口人数

- `GET /staffing/alerts`
  - 支持按日期、产线、状态、严重程度筛选

- `POST /staffing/shift-plans/{id}/recalculate-coverage`
  - 手动触发重算

### 实施阶段

#### 第一阶段

- 按排班计划计算人数缺口
- 显示未满编状态

#### 第二阶段

- 引入资格覆盖率
- 引入关键岗位空岗预警

#### 第三阶段

- 与风险模块打通
- 支持自动推荐替补员工

---

## 7. 路线图四：资质到期与复训闭环

### 模块改动点

- `qualification`
  - 增加到期预警规则
  - 增加复训任务跟踪
- `staffing`
  - 识别受影响排班
- `risk`
  - 对高风险到期情况自动建风险

### 数据模型补充

- 在 `Certification`、`SafetyTraining`、`EquipmentAuthorization` 相关对象基础上补充：
  - `warning_days`
  - `grace_period_days`

- 新增 `QualificationAlert`
  - `worker_id`
  - `qualification_type`
  - `qualification_record_id`
  - `alert_level`
  - `expires_at`
  - `status`

- 新增 `RetrainingTask`
  - `worker_id`
  - `training_id`
  - `source_alert_id`
  - `due_date`
  - `task_status`

### 接口建议

- `GET /qualification/alerts`
- `POST /qualification/alerts/recalculate`
- `POST /qualification/retraining-tasks`
- `GET /qualification/workers/{worker_id}/expiring-items`

### 实施阶段

#### 第一阶段

- 实现到期前预警
- 输出受影响员工名单

#### 第二阶段

- 自动关联未来排班与工位资格
- 生成复训任务

#### 第三阶段

- 复训完成后自动关闭预警
- 联动恢复上岗资格

---

## 8. 路线图五：排班、考勤、请假的自动对账

### 模块改动点

- `attendance`
  - 增加对账服务与异常识别
- `staffing`
  - 输出标准化排班执行口径
- `risk`
  - 接收严重出勤异常

### 数据模型补充

- 新增 `AttendanceException`
  - `worker_id`
  - `work_date`
  - `exception_type`
  - `shift_assignment_id`
  - `attendance_record_id`
  - `leave_request_id`
  - `severity`
  - `status`
  - `resolution_notes`

### 接口建议

- `GET /attendance/exceptions`
- `POST /attendance/reconcile/daily`
- `GET /attendance/workers/{worker_id}/reconciliation`

### 实施阶段

#### 第一阶段

- 识别“已排班未出勤”“已请假仍排班”

#### 第二阶段

- 识别“未排班有出勤”“请假仍出勤”

#### 第三阶段

- 与薪资规则、风险规则联动

---

## 9. 路线图六：风险信号自动触发

### 模块改动点

- `risk`
  - 增加规则触发引擎
- `staffing`、`attendance`、`qualification`
  - 输出标准化异常事件

### 数据模型补充

- 新增 `RiskRule`
  - `code`
  - `name`
  - `trigger_source`
  - `severity`
  - `enabled`

- 新增 `RiskEvent`
  - `rule_id`
  - `source_type`
  - `source_id`
  - `payload`
  - `triggered_at`

### 接口建议

- `GET /risk/rules`
- `POST /risk/rules`
- `POST /risk/signals/trigger`
- `GET /risk/events`

### 实施阶段

#### 第一阶段

- 先实现规则编码在服务层
- 覆盖无资格上岗、缺编开线、证书过期仍排班

#### 第二阶段

- 抽象统一规则配置
- 支持按规则启停

#### 第三阶段

- 与复核流、通知流、Agent 问答联动

---

## 10. 路线图七：调班、替岗、支援流程化

### 模块改动点

- `staffing`
  - 新增排班变更流程模型
- `workforce`
  - 衔接员工归属与支援来源
- `qualification`
  - 变更后二次资格校验

### 数据模型补充

- 新增 `ShiftChangeRequest`
  - `request_type`
  - `original_assignment_id`
  - `requester_worker_id`
  - `target_worker_id`
  - `reason`
  - `status`
  - `approved_by`
  - `approved_at`

- 新增 `SupportAssignment`
  - `worker_id`
  - `source_line_id`
  - `target_line_id`
  - `source_team_id`
  - `target_team_id`
  - `support_date`
  - `status`

### 接口建议

- `POST /staffing/shift-change-requests`
- `POST /staffing/shift-change-requests/{id}/approve`
- `GET /staffing/support-assignments`

### 实施阶段

#### 第一阶段

- 记录调班申请与审批

#### 第二阶段

- 支持替岗与跨线支援

#### 第三阶段

- 变更后自动刷新资格、冲突与风险状态

---

## 11. 路线图八：面向订单的人力匹配与排班建议

### 模块改动点

- `production`
  - 输出订单工序能力需求
- `staffing`
  - 新增候选推荐服务
- `capability`、`qualification`
  - 输出员工画像标签

### 数据模型补充

- 新增 `StaffingRecommendation`
  - `shift_plan_id`
  - `worker_id`
  - `score`
  - `match_reasons`
  - `risk_flags`

- 可新增 `WorkerCapabilityProfile`
  - `worker_id`
  - `skill_score`
  - `qualification_score`
  - `availability_score`
  - `support_history_score`

### 接口建议

- `GET /staffing/shift-plans/{id}/recommendations`
- `GET /production/orders/{id}/staffing-gap-analysis`

### 实施阶段

#### 第一阶段

- 基于资格通过/不通过给出候选池

#### 第二阶段

- 增加评分排序

#### 第三阶段

- 增加按策略推荐，例如优先本班组、优先低风险、优先熟练工

---

## 12. 路线图九：自动薪资计算

### 模块改动点

- `attendance`
  - 增加薪资草算逻辑
- `staffing`
  - 提供班次津贴、夜班、支援等口径
- `workforce`
  - 输出员工用工类型与基础薪酬口径

### 数据模型补充

- 新增 `PayrollRule`
  - `employment_type`
  - `overtime_rate`
  - `night_shift_allowance`
  - `leave_deduction_rule`
  - `support_subsidy_rule`

- 新增 `PayrollCalculationDetail`
  - `payroll_record_id`
  - `source_type`
  - `source_id`
  - `amount`
  - `calculation_rule`

### 接口建议

- `POST /attendance/payroll/calculate`
- `GET /attendance/payroll/{id}/details`
- `POST /attendance/payroll/recalculate`

### 实施阶段

#### 第一阶段

- 先输出薪资草案，不直接替代人工确认

#### 第二阶段

- 支持按用工类型套用不同规则

#### 第三阶段

- 结合异常考勤自动挂起待确认项

---

## 13. 推荐实施顺序

从投入产出比和模块联动关系来看，建议采用以下实施顺序：

### 第一阶段：先补“硬约束”

1. 上岗资格自动判定
2. 排班可用性与冲突校验
3. 缺编、错配与关键岗位空岗预警

阶段目标：

- 让排班结果具备基本业务可执行性
- 减少明显错误排班进入执行层

### 第二阶段：再补“执行闭环”

4. 资质到期与复训闭环
5. 排班、考勤、请假的自动对账
6. 风险信号自动触发
7. 调班、替岗、支援流程化

阶段目标：

- 让系统具备从计划、执行到异常处理的完整链路

### 第三阶段：最后补“决策辅助与核算自动化”

8. 面向订单的人力匹配与排班建议
9. 自动薪资计算

阶段目标：

- 将系统从运营执行平台升级为运营决策平台

## 14. 建议的设计原则

为避免后续业务逻辑分散、重复和难以维护，建议在实施过程中遵循以下原则：

- 资格判定、排班冲突、风险触发都应沉淀为独立领域服务，而不是散落在路由层
- 尽量输出结构化“判定结果”和“原因码”，而不是只返回文本错误
- 先做同步校验，再逐步演进到异步重算和批量分析
- 所有自动识别出的异常，都尽量保留快照与触发来源，方便追溯
- 风险、预警、异常、建议四类对象应区分清楚，避免语义混用

## 15. 总结

当前系统最值得增强的方向，不是继续扩展更多基础台账，而是补上制造现场真正高价值的业务判断与运营闭环。

如果按优先级推进，最先应落地的不是“更复杂的页面”，而是以下三件事：

1. 上岗资格自动判定
2. 排班可用性与冲突校验
3. 排班达成度与异常预警

这三类能力一旦完成，系统就会从“记录型系统”明显升级为“运营控制型系统”，后续再叠加风险自动触发、调班流程和智能排班建议，整体产品竞争力会更强。
