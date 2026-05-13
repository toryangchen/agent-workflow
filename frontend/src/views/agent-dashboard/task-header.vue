<script setup lang="ts">
import type { TaskSnapshot } from '../../types/agent'

defineProps<{ task: TaskSnapshot }>()
</script>

<template>
  <section class="task-header">
    <div>
      <span class="label">任务ID</span>
      <strong>{{ task.task_id.slice(0, 18) }}</strong>
    </div>
    <div>
      <span class="label">项目</span>
      <strong>{{ task.project_id ?? '-' }}</strong>
    </div>
    <div>
      <span class="label">错误码</span>
      <strong>{{ task.error_code ?? '-' }}</strong>
    </div>
    <div>
      <span class="label">开始时间</span>
      <strong>2024-05-13 15:21:10</strong>
    </div>
    <div>
      <span class="label">总耗时</span>
      <strong>{{ task.status === 'success' ? '1分 32秒' : '--' }}</strong>
    </div>
  </section>
</template>

<style scoped>
.task-header {
  display: grid;
  grid-template-columns: 1.2fr 1fr 1fr 1fr 0.8fr;
  gap: 12px;
  padding: 18px 24px;
  border: 1px solid #d9e1ec;
  border-radius: 8px;
  background: #fff;
}

.task-header > div {
  min-width: 0;
}

.label {
  display: block;
  margin-bottom: 8px;
  color: #4b5563;
  font-size: 14px;
}

strong {
  display: block;
  overflow: hidden;
  color: #111827;
  font-size: 16px;
  font-weight: 520;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 900px) {
  .task-header {
    grid-template-columns: 1fr;
  }
}
</style>
