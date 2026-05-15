<template>
  <div class="chat-window">
    <MessageList v-if="store.isLoadingMessages || msgs.length > 0" />
    <WelcomeScreen v-else @select="handleSuggestion" />
    <ChatInput />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useChatStore } from '../stores/chat'
import WelcomeScreen from './WelcomeScreen.vue'
import MessageList from './MessageList.vue'
import ChatInput from './ChatInput.vue'

const store = useChatStore()
const msgs = computed(() => store.currentMessages())

function handleSuggestion(text: string) {
  store.sendMessage(text)
}
</script>

<style scoped lang="scss">
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--chat-bg);
}
</style>
