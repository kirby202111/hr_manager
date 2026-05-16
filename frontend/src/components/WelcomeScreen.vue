<template>
  <div class="welcome-screen">
    <el-icon :size="48" color="#409eff"><ChatDotRound /></el-icon>
    <h2>生产智能助手</h2>
    <p class="welcome-desc">我可以帮助您查询员工信息、考勤记录、薪资数据等，请选择下方问题或直接输入</p>
    <div class="suggestion-chips">
      <el-button
        v-for="chip in suggestions"
        :key="chip"
        round
        @click="$emit('select', chip)"
      >
        {{ chip }}
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ChatDotRound } from '@element-plus/icons-vue'

defineEmits<{ select: [text: string] }>()

const suggestions = [
  '查询员工信息',
  '查看考勤记录',
  '提交请假申请',
  '薪资查询',
]
</script>

<style scoped lang="scss">
.welcome-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 40px 20px;
  text-align: center;

  h2 {
    margin: 16px 0 8px;
    font-size: 22px;
    font-weight: 600;
  }

  .welcome-desc {
    color: var(--chat-text-secondary);
    font-size: 14px;
    max-width: 360px;
    margin-bottom: 24px;
  }

  .suggestion-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    justify-content: center;
  }
}
</style>
