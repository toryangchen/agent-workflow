<script setup lang="ts">
import { computed } from 'vue'
import type { AgentEvent, TaskSnapshot } from '../../types/agent'

const props = defineProps<{ task: TaskSnapshot; events: AgentEvent[] }>()

const startedAt = computed(() => props.events.find((event) => event.type === 'task_started')?.timestamp)
const endedAt = computed(
  () =>
    [...props.events]
      .reverse()
      .find((event) => event.type === 'task_completed' || event.type === 'task_failed')?.timestamp,
)

const startedAtText = computed(() =>
  startedAt.value ? new Date(startedAt.value).toLocaleString('zh-CN', { hour12: false }) : '--',
)

const totalDuration = computed(() => {
  if (!startedAt.value) return '--'
  const end = endedAt.value ?? new Date().toISOString()
  return formatDuration(new Date(end).getTime() - new Date(startedAt.value).getTime())
})

function formatDuration(ms: number) {
  const totalSeconds = Math.max(0, Math.round(ms / 1000))
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  if (minutes === 0) return `${seconds}秒`
  return `${minutes}分 ${seconds}秒`
}
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
      <strong>{{ startedAtText }}</strong>
    </div>
    <div>
      <span class="label">总耗时</span>
      <strong>{{ totalDuration }}</strong>
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
