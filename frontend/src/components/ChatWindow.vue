<template>
  <div class="chat-window">
    <OnboardingSummaryPanel :summary="activeOnboardingCase" />
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
import OnboardingSummaryPanel from './OnboardingSummaryPanel.vue'

const store = useChatStore()
const msgs = computed(() => store.currentMessages())
const activeOnboardingCase = computed(() => {
  if (!store.currentSessionId) return null
  return store.onboardingCases[store.currentSessionId] || null
})

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
