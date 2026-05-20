<template>
  <div class="tool-call-badge">
    <el-tag
      v-for="(tc, idx) in toolCalls"
      :key="idx"
      :type="tc.status === 'calling' ? 'warning' : 'success'"
      size="small"
      round
      class="badge-tag"
    >
      <el-icon v-if="tc.status === 'calling'" class="is-loading"><Loading /></el-icon>
      <el-icon v-else><CircleCheck /></el-icon>
      {{ tc.status === 'calling' ? '执行中' : '已完成' }}: {{ tc.names.map(labelForTool).join('、') }}
    </el-tag>
  </div>
</template>

<script setup lang="ts">
import { Loading, CircleCheck } from '@element-plus/icons-vue'
import type { ToolCallInfo } from '../types/chat'

defineProps<{
  toolCalls: ToolCallInfo[]
}>()

const TOOL_LABELS: Record<string, string> = {
  find_worker_candidates: '查重候选',
  create_worker_profile: '创建员工',
  update_worker_profile: '更新员工',
  create_primary_assignment: '创建任职归属',
  update_primary_assignment: '更新任职归属',
  list_shopfloor_targets: '查询产线/工位',
  get_workstation_requirements: '读取工位要求',
  get_worker_qualification_summary: '读取资质摘要',
  record_worker_skill: '登记技能',
  record_worker_certification: '登记证书',
  record_worker_training: '登记培训',
  record_equipment_authorization: '登记设备授权',
  check_worker_workstation_eligibility: '上岗资格复核',
  load_onboarding_case: '读取入职摘要',
  save_onboarding_case: '保存入职摘要',
  clear_onboarding_case: '清空入职摘要',
}

function labelForTool(name: string) {
  return TOOL_LABELS[name] || name
}
</script>

<style scoped lang="scss">
.tool-call-badge {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 6px 0;
}

.badge-tag {
  .el-icon { margin-right: 4px; }
}
</style>
