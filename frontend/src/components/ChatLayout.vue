<template>
  <div class="chat-layout">
    <aside class="chat-sidebar">
      <slot name="sidebar" />
    </aside>
    <main class="chat-main">
      <slot name="main" />
    </main>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped lang="scss">
.chat-layout {
  display: flex;
  height: 100%;
  width: 100%;
}

.chat-sidebar {
  width: var(--chat-sidebar-width);
  min-width: var(--chat-sidebar-width);
  background: var(--chat-sidebar-bg);
  border-right: 1px solid var(--chat-border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}
</style>
