<template>
  <div class="session-sidebar">
    <div class="sidebar-header">
      <span class="sidebar-title">对话管理</span>
      <el-button :icon="Plus" circle size="small" @click="handleCreate" />
    </div>
    <div class="user-tag-selector">
      <el-input
        v-model="localUserTag"
        size="small"
        placeholder="用户标识"
        clearable
        @change="handleUserTagChange"
        @keyup.enter="handleUserTagChange"
      />
    </div>
    <div class="session-list">
      <div
        v-for="sid in sessions"
        :key="sid"
        class="session-item"
        :class="{ active: sid === currentSessionId }"
        @click="selectSession(sid)"
      >
        <el-icon class="session-icon"><ChatDotRound /></el-icon>
        <span class="session-label">{{ getSessionLabel(sid) }}</span>
        <el-button
          class="delete-btn"
          :icon="Delete"
          circle
          size="small"
          text
          @click.stop="handleDelete(sid)"
        />
      </div>
    </div>
    <div class="sidebar-footer">
      <el-button text @click="showSkills = true">
        <el-icon><Setting /></el-icon>
        <span>技能管理</span>
      </el-button>
    </div>
    <SkillPanel v-model:visible="showSkills" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { Plus, Delete, ChatDotRound, Setting } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import { useChatStore } from '../stores/chat'
import SkillPanel from './SkillPanel.vue'

const store = useChatStore()
const { sessions, currentSessionId, messages, userTag } = storeToRefs(store)
const { selectSession, createSession, deleteSession } = store

const showSkills = ref(false)
const localUserTag = ref(userTag.value)

watch(userTag, (val) => {
  localUserTag.value = val
})

function getSessionLabel(sid: string): string {
  const msgs = messages.value[sid]
  if (msgs && msgs.length > 0) {
    const first = msgs.find(m => m.role === 'user')
    if (first) return first.content.slice(0, 20) + (first.content.length > 20 ? '...' : '')
  }
  return sid.slice(0, 8) + '...'
}

function handleCreate() {
  createSession()
}

async function handleUserTagChange() {
  await store.setUserTag(localUserTag.value)
}

async function handleDelete(sid: string) {
  try {
    await ElMessageBox.confirm('确定删除该对话？', '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteSession(sid)
  } catch { /* cancelled */ }
}
</script>

<style scoped lang="scss">
.session-sidebar {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid var(--chat-border);
}

.sidebar-title {
  font-weight: 600;
  font-size: 15px;
}

.user-tag-selector {
  padding: 10px 16px;
  border-bottom: 1px solid var(--chat-border);
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 2px;

  &:hover { background: #f5f7fa; }
  &.active { background: #ecf5ff; color: #409eff; }

  .session-icon { flex-shrink: 0; }
  .session-label {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 13px;
  }
  .delete-btn { flex-shrink: 0; opacity: 0; transition: opacity 0.2s; }
  &:hover .delete-btn { opacity: 1; }
}

.sidebar-footer {
  border-top: 1px solid var(--chat-border);
  padding: 8px;

  .el-button { width: 100%; justify-content: flex-start; }
}
</style>
