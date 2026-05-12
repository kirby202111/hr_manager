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
      {{ tc.status === 'calling' ? '正在调用' : '已调用' }}: {{ tc.names.join(', ') }}
    </el-tag>
  </div>
</template>

<script setup lang="ts">
import { Loading, CircleCheck } from '@element-plus/icons-vue'
import type { ToolCallInfo } from '../types/chat'

defineProps<{
  toolCalls: ToolCallInfo[]
}>()
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
