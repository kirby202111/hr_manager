<template>
  <div class="chat-input">
    <el-input
      v-model="text"
      type="textarea"
      :autosize="{ minRows: 1, maxRows: 4 }"
      placeholder="输入您的问题… (Enter 发送，Shift+Enter 换行)"
      :disabled="isStreaming"
      @keydown="handleKeydown"
    />
    <el-button
      v-if="isStreaming"
      type="danger"
      circle
      class="send-btn"
      @click="stopStreaming"
    >
      <el-icon><VideoPause /></el-icon>
    </el-button>
    <el-button
      v-else
      type="primary"
      circle
      class="send-btn"
      :disabled="!text.trim()"
      @click="handleSend"
    >
      <el-icon><Promotion /></el-icon>
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Promotion, VideoPause } from '@element-plus/icons-vue'
import { useChatStore } from '../stores/chat'

const store = useChatStore()
const isStreaming = store.isStreaming
const sendMessage = store.sendMessage
const stopStreaming = store.stopStreaming

const text = ref('')

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

function handleSend() {
  if (!text.value.trim()) return
  sendMessage(text.value)
  text.value = ''
}

defineExpose({ setText: (val: string) => { text.value = val } })
</script>

<style scoped lang="scss">
.chat-input {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 12px 20px 16px;
  background: #fff;
  border-top: 1px solid var(--chat-border);

  :deep(.el-textarea__inner) {
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 14px;
  }

  .send-btn {
    flex-shrink: 0;
    width: 36px;
    height: 36px;
  }
}
</style>
