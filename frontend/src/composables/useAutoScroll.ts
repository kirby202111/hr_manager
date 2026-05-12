import { ref, watch, nextTick, type Ref } from 'vue'

export function useAutoScroll(containerRef: Ref<HTMLDivElement | null>, trigger: Ref<unknown>) {
  const userScrolledUp = ref(false)

  function onScroll() {
    const el = containerRef.value
    if (!el) return
    const distFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight
    userScrolledUp.value = distFromBottom > 80
  }

  watch(trigger, async () => {
    if (userScrolledUp.value) return
    await nextTick()
    const el = containerRef.value
    if (el) el.scrollTop = el.scrollHeight
  }, { flush: 'post' })

  return { onScroll }
}
