<template>
  <div ref="scrollContainer" class="message-list" @scroll="onScroll">
    <MessageItem v-for="msg in msgs" :key="msg.id" :message="msg" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
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
</style>
