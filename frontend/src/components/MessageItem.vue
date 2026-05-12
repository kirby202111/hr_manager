<template>
  <div class="message-item" :class="[`message-${message.role}`, { 'is-error': message.isError }]">
    <div class="message-avatar">
      <el-avatar v-if="message.role === 'user'" :size="32" :icon="User" />
      <el-avatar v-else :size="32" style="background: #409eff">
        <el-icon><Monitor /></el-icon>
      </el-avatar>
    </div>
    <div class="message-body">
      <ToolCallBadge
        v-if="message.toolCalls && message.toolCalls.length > 0"
        :tool-calls="message.toolCalls"
      />
      <div v-if="message.role === 'user'" class="message-content user-content">
        {{ message.content }}
      </div>
      <div v-else class="message-content assistant-content markdown-body" v-html="renderedContent" />
      <div v-if="message.isStreaming && !message.content" class="typing-indicator">
        <span /><span /><span />
      </div>
      <div v-if="message.isStreaming && message.content" class="streaming-cursor">▎</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { User, Monitor } from '@element-plus/icons-vue'
import MarkdownIt from 'markdown-it'
import type { ChatMessage } from '../types/chat'
import ToolCallBadge from './ToolCallBadge.vue'
import '../styles/markdown.scss'

const props = defineProps<{ message: ChatMessage }>()

const md = new MarkdownIt({ html: false, breaks: true, linkify: true })

const renderedContent = computed(() => {
  if (props.message.role !== 'assistant') return ''
  return md.render(props.message.content || '')
})
</script>

<style scoped lang="scss">
.message-item {
  display: flex;
  gap: 12px;
  padding: 16px 20px;

  &.message-user {
    flex-direction: row-reverse;

    .message-body { align-items: flex-end; }
    .message-content {
      background: var(--chat-user-bubble);
      color: #fff;
      border-radius: 12px 12px 2px 12px;
    }
  }

  &.message-assistant {
    .message-content {
      background: var(--chat-assistant-bubble);
      color: var(--chat-text);
      border-radius: 12px 12px 12px 2px;
      border: 1px solid var(--chat-border);
    }
  }

  &.is-error .message-content {
    border-color: #f56c6c;
  }
}

.message-avatar { flex-shrink: 0; margin-top: 2px; }

.message-body {
  display: flex;
  flex-direction: column;
  max-width: var(--chat-max-width-bubble);
  min-width: 0;
}

.message-content {
  padding: 10px 14px;
  line-height: 1.6;
  font-size: 14px;
  word-break: break-word;

  :deep(table) { margin: 4px 0; }
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 10px 14px;

  span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #c0c4cc;
    animation: bounce 1.4s infinite both;

    &:nth-child(2) { animation-delay: 0.2s; }
    &:nth-child(3) { animation-delay: 0.4s; }
  }
}

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

.streaming-cursor {
  color: #409eff;
  animation: blink 1s step-end infinite;
  font-size: 14px;
}

@keyframes blink {
  50% { opacity: 0; }
}
</style>
