<template>
  <section v-if="summary" class="summary-panel">
    <div class="summary-header">
      <div>
        <div class="summary-eyebrow">Onboarding</div>
        <h2 class="summary-title">{{ title }}</h2>
      </div>
      <el-tag :type="statusTagType" size="small" effect="plain">{{ statusLabel }}</el-tag>
    </div>

    <p v-if="summary.last_agent_summary" class="summary-copy">{{ summary.last_agent_summary }}</p>

    <div class="summary-grid">
      <div class="summary-item">
        <span class="summary-label">员工</span>
        <span class="summary-value">{{ workerLabel }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">归属</span>
        <span class="summary-value">{{ assignmentLabel }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">工位</span>
        <span class="summary-value">{{ workstationLabel }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">最近复核</span>
        <span class="summary-value">{{ eligibilityLabel }}</span>
      </div>
    </div>

    <div v-if="summary.completed_actions.length > 0" class="summary-block">
      <div class="summary-label">已完成</div>
      <div class="pill-list">
        <span v-for="item in summary.completed_actions" :key="item" class="pill success">{{ item }}</span>
      </div>
    </div>

    <div v-if="summary.missing_fields.length > 0" class="summary-block">
      <div class="summary-label">缺失字段</div>
      <div class="pill-list">
        <span v-for="item in summary.missing_fields" :key="item" class="pill warning">{{ labelForField(item) }}</span>
      </div>
    </div>

    <div v-if="summary.pending_actions.length > 0" class="summary-block">
      <div class="summary-label">阻塞 / 下一步</div>
      <ul class="summary-list">
        <li v-for="item in summary.pending_actions" :key="item">{{ item }}</li>
      </ul>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { OnboardingCaseSummary } from '../types/chat'

const props = defineProps<{
  summary: OnboardingCaseSummary | null
}>()

const FIELD_LABELS: Record<string, string> = {
  worker_code: '工号',
  worker_name: '姓名',
  employment_type: '用工类型',
  organization_unit_id: '组织单元',
  production_line_id: '产线',
  production_team_id: '班组',
  role_title: '岗位名称',
  hire_date: '入职日期',
  target_workstation_id: '目标工位',
}

const title = computed(() => props.summary?.worker_name || props.summary?.worker_code || '现场入职')

const statusLabel = computed(() => {
  const status = props.summary?.latest_eligibility?.status
  if (status === 'eligible') return '可上岗'
  if (status === 'warning') return '待关注'
  if (props.summary?.is_active) return '办理中'
  return '待开始'
})

const statusTagType = computed(() => {
  const status = props.summary?.latest_eligibility?.status
  if (status === 'eligible') return 'success'
  if (status === 'warning') return 'warning'
  return 'info'
})

const workerLabel = computed(() => {
  if (!props.summary) return '-'
  const parts = [props.summary.worker_name, props.summary.worker_code].filter(Boolean)
  return parts.length > 0 ? parts.join(' / ') : '-'
})

const assignmentLabel = computed(() => {
  if (!props.summary) return '-'
  const parts = [
    props.summary.organization_unit_name,
    props.summary.production_line_name,
    props.summary.production_team_name,
    props.summary.role_title,
  ].filter(Boolean)
  return parts.length > 0 ? parts.join(' / ') : '-'
})

const workstationLabel = computed(() => {
  if (!props.summary) return '-'
  return props.summary.target_workstation_name || props.summary.target_workstation_id?.toString() || '-'
})

const eligibilityLabel = computed(() => {
  if (!props.summary?.latest_eligibility) return '未复核'
  return props.summary.latest_eligibility.summary_reason || props.summary.latest_eligibility.status || '未复核'
})

function labelForField(field: string) {
  return FIELD_LABELS[field] || field
}
</script>

<style scoped lang="scss">
.summary-panel {
  border-bottom: 1px solid var(--chat-border);
  background: #fff;
  padding: 18px 20px 16px;
}

.summary-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.summary-eyebrow {
  font-size: 11px;
  color: var(--chat-text-secondary);
  text-transform: uppercase;
}

.summary-title {
  margin: 4px 0 0;
  font-size: 18px;
  line-height: 1.2;
  color: var(--chat-text);
}

.summary-copy {
  margin: 10px 0 0;
  color: var(--chat-text-secondary);
  font-size: 13px;
  line-height: 1.5;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 18px;
  margin-top: 14px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.summary-label {
  font-size: 12px;
  color: var(--chat-text-secondary);
}

.summary-value {
  font-size: 13px;
  line-height: 1.4;
  color: var(--chat-text);
  word-break: break-word;
}

.summary-block {
  margin-top: 14px;
}

.pill-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.pill {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 8px;
  font-size: 12px;
  line-height: 1.3;
}

.pill.success {
  background: #effaf4;
  color: #177245;
}

.pill.warning {
  background: #fff7e6;
  color: #9b6200;
}

.summary-list {
  margin: 8px 0 0;
  padding-left: 18px;
  color: var(--chat-text);
  font-size: 13px;
  line-height: 1.6;
}

@media (max-width: 900px) {
  .summary-grid {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
