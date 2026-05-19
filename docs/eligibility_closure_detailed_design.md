# 上岗资格自动判定逻辑闭环详细设计

## 1. 背景

当前系统已经具备以下能力：

- 工位资格要求维护
- 工序资格要求维护
- 员工资格判定服务
- 排班创建/更新前的资格校验
- 资格快照留痕与查询

但在业务闭环上仍存在三个缺口：

1. 手工资格校验时，`production_operation_id` 与 `workstation_id` 的归属关系未被强约束。
2. 带生产订单的排班场景中，若工位无法唯一解析到工序，系统会出现静默退化风险。
3. 排班创建/更新接口会返回资格摘要，但排班查询接口不能稳定回看最新资格结果。

本设计只解决以上三个缺口，不扩展到排班冲突、风险联动、复训预警等后续能力。

## 2. 当前关系模型

### 2.1 工序与工位关系

当前系统采用“工序从属于工位”的建模方式：

- `ProductionOperation.workstation_id` 表示工序记录中保存的执行工位 ID
- `Workstation.operations` 表示工位下的工序集合

业务语义如下：

- 工位承载基础资格要求
- 工序承载该工位下的附加资格要求
- 最终资格判定结果由工位要求与工序要求合并得到

### 2.2 排班与工序关系

`ShiftAssignment` 当前只直接关联：

- `shift_plan_id`
- `worker_id`
- `workstation_id`

排班实体本身不保存 `production_operation_id`。因此，排班场景中的工序上下文依赖运行时解析和资格快照留痕。

## 3. 目标状态

### 3.1 手工校验入口的工序上下文成为硬约束

- `POST /staffing/eligibility/check` 若未传 `production_operation_id`，只按工位要求判定。
- 若传了 `production_operation_id`，系统必须校验：
  - 工序存在
  - 工序属于当前 `workstation_id`
- 若工序不属于工位，直接返回业务校验错误，不写资格快照。

### 3.2 带订单排班必须解析到唯一工序

- `ShiftPlan.production_order_id` 为空时，允许只按工位要求判定。
- `ShiftPlan.production_order_id` 不为空时，必须在当前订单下、当前工位下解析到唯一有效工序。
- 若没有匹配工序，返回 `blocked`。
- 若匹配到多个工序，返回 `blocked`。
- 不再使用“选最早 sequence 的工序继续执行”或“退化成只按工位判定”的策略。

### 3.3 排班侧查询结果必须可回查

以下接口统一返回资格摘要字段：

- 排班创建
- 排班更新
- 排班单条查询
- 排班列表查询

摘要字段保持不变：

- `eligibility_status`
- `eligibility_summary_reason`
- `eligibility_snapshot_id`

查询接口只读取快照，不做在线重算。

### 3.4 快照成为最终事实源

- 所有参与排班创建/更新决策的资格结果必须落快照。
- 快照中的 `status`、`summary_reason`、`detail_json` 必须与最终对外响应一致。
- 排班回查只读取快照摘要，不拼装临时状态。

## 4. 详细方案

### 4.1 手工资格校验链路

入口：`POST /staffing/eligibility/check`

处理流程：

1. 校验 `worker_id` 存在。
2. 校验 `workstation_id` 存在。
3. 若未传 `production_operation_id`，直接进入资格要求合并与判定。
4. 若传入 `production_operation_id`：
   - 校验工序存在
   - 校验 `ProductionOperation.workstation_id == workstation_id`
   - 不满足时返回业务校验错误
5. 只有通过上下文校验后，才允许合并工位要求与工序要求并生成快照。

错误口径：

- 工序不存在：`not_found`
- 工序不属于工位：`validation_error`，`error_code = operation_workstation_mismatch`

### 4.2 排班创建/更新链路

入口：

- `create_shift_assignment()`
- `update_shift_assignment()`

处理流程：

1. 校验 `shift_plan`、`worker`、`workstation` 存在。
2. 若 `shift_plan.production_order_id` 为空：
   - 不解析工序
   - 只按工位要求判定
3. 若 `shift_plan.production_order_id` 不为空：
   - 查询当前订单下、当前工位下的候选工序
   - 仅将 `planned`、`released`、`active` 视为有效工序状态
4. 分支处理：
   - 1 条候选工序：进入正常资格判定
   - 0 条候选工序：返回 `blocked`
   - 多条候选工序：返回 `blocked`
5. `blocked` 场景仍需写快照，但不允许创建/更新排班。
6. `warning` / `eligible` 场景先写快照，再写排班，最后回填 `shift_assignment_id`。

新增原因码：

- `MISSING_OPERATION_CONTEXT`
- `AMBIGUOUS_OPERATION_CONTEXT`

原因语义：

- `MISSING_OPERATION_CONTEXT`：生产订单下不存在当前工位的工序
- `AMBIGUOUS_OPERATION_CONTEXT`：生产订单下当前工位命中了多条候选工序

### 4.3 快照一致性规则

快照来源：

- 手工校验：`manual_check`
- 排班新增：`assignment_create`
- 排班更新：`assignment_update`

一致性要求：

- 若排班场景因为工序缺失或歧义被阻断，快照中必须记录最终 `blocked` 结果。
- 不允许先写“可通过”的快照，再在响应层改写为阻断或预警。
- 若资格判定最终可通过，快照与排班写接口返回值必须一致。

### 4.4 排班回查链路

排班查询接口通过 `shift_assignment_id` 关联 `WorkerEligibilitySnapshot`。

回查规则：

- 同一排班若存在多条快照，取最新一条
- 最新定义：`checked_at desc, id desc`
- 若排班没有任何关联快照，资格摘要字段返回 `null`

职责分工：

- 排班接口：返回快照摘要，面向执行和列表浏览
- 快照接口：返回完整判定明细，面向审计和追溯

## 5. 接口影响

### 5.1 行为变更

- `POST /staffing/eligibility/check`
  - 传入工序时新增工序-工位归属校验
- 排班创建/更新接口
  - 带订单时新增“唯一工序解析”前置约束
- 排班查询接口
  - 补齐资格摘要回查能力

### 5.2 返回结构

`ShiftAssignmentResponse` 不新增字段，继续使用：

- `eligibility_status`
- `eligibility_summary_reason`
- `eligibility_snapshot_id`

## 6. 验收与测试

### 6.1 手工校验

- 工位与工序匹配时返回正常判定
- 工序不存在时返回失败
- 工序属于其他工位时返回失败
- 工序与工位不匹配时不写快照

### 6.2 排班创建/更新

- 无生产订单时按工位要求正常判定
- 带生产订单且唯一匹配工序时正常判定并写快照
- 带生产订单但无匹配工序时返回 `blocked`，不写排班，写阻断快照
- 带生产订单且多个匹配工序时返回 `blocked`，不写排班，写阻断快照

### 6.3 排班回查

- 创建成功后单条查询可回看资格摘要
- 创建成功后列表查询可回看资格摘要
- 同一排班多次更新后回看最新快照摘要
- 历史无快照排班返回空摘要字段

### 6.4 快照一致性

- 排班写接口返回的 `status / summary_reason / snapshot_id` 与快照记录一致
- 缺失工序、歧义工序场景的 `detail_json` 包含新增原因码
