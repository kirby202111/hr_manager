<template>
  <ChatLayout>
    <template #sidebar>
      <SessionSidebar />
    </template>
    <template #main>
      <ChatWindow />
    </template>
  </ChatLayout>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import ChatLayout from '../components/ChatLayout.vue'
import SessionSidebar from '../components/SessionSidebar.vue'
import ChatWindow from '../components/ChatWindow.vue'
import { useChat } from '../composables/useChat'

const { init } = useChat()
onMounted(init)
</script>
