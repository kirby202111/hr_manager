<template>
  <el-drawer
    :model-value="visible"
    title="技能管理"
    direction="ltr"
    size="320px"
    @update:model-value="$emit('update:visible', $event)"
    @open="fetchSkills"
  >
    <div v-loading="loading" class="skill-list">
      <div v-for="skill in skills" :key="skill.name" class="skill-item">
        <div class="skill-info">
          <div class="skill-name">{{ skill.name }}</div>
          <div class="skill-desc">{{ skill.description }}</div>
        </div>
        <el-switch
          :model-value="skill.enabled"
          @change="(val: boolean) => toggleSkill(skill.name, val)"
        />
      </div>
      <el-empty v-if="!loading && skills.length === 0" description="暂无可用技能" />
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { useSkillsStore } from '../stores/skills'

defineProps<{ visible: boolean }>()
defineEmits<{ 'update:visible': [val: boolean] }>()

const store = useSkillsStore()
const skills = store.skills
const loading = store.loading
const fetchSkills = store.fetchSkills
const toggleSkill = store.toggleSkill
</script>

<style scoped lang="scss">
.skill-list {
  padding: 0 4px;
}

.skill-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--chat-border);

  &:last-child { border-bottom: none; }
}

.skill-info {
  flex: 1;
  min-width: 0;
}

.skill-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 2px;
}

.skill-desc {
  font-size: 12px;
  color: var(--chat-text-secondary);
  line-height: 1.4;
}
</style>
