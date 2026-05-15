<template>
  <div ref="scrollContainer" class="message-list" @scroll="onScroll">
    <div v-if="store.isLoadingMessages" class="loading-messages">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载历史消息...</span>
    </div>
    <MessageItem v-for="msg in msgs" :key="msg.id" :message="msg" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { useChatStore } from '../stores/chat'
import { useAutoScroll } from '../composables/useAutoScroll'
import MessageItem from './MessageItem.vue'

const store = useChatStore()
const msgs = computed(() => store.currentMessages())
const trigger = computed(() => {
  const list = store.currentMessages()
  const last = list[list.length - 1]
  return last ? `${last.id}:${last.content.length}:${last.isStreaming}` : ''
})

const scrollContainer = ref<HTMLDivElement | null>(null)
const { onScroll } = useAutoScroll(scrollContainer, trigger)
</script>

<style scoped lang="scss">
.message-list {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 16px;
}

.loading-messages {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  color: #909399;
  font-size: 13px;
}
</style>
