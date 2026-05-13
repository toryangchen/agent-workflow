<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import TaskHeader from './task-header.vue'
import WorkflowTimeline from './timeline.vue'
import RootCause from './root-cause.vue'
import { useAgentStore } from '../../stores/agent'

const store = useAgentStore()
const projectId = ref('payment-service-prod')
const errorCode = ref('JAVA_HEAP_OOM')
const description = ref('最近 Redis timeout 很严重，伴随请求变慢和 JVM 内存上涨')
const userInput = computed(() => `${projectId.value} ${description.value}，错误码 ${errorCode.value}`)

async function submitTask() {
  if (!projectId.value.trim() || !errorCode.value.trim()) {
    ElMessage.warning('请输入 project_id 和 error_code')
    return
  }
  try {
    await store.submit(userInput.value)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '任务创建失败')
  }
}
</script>

<template>
  <main class="dashboard">
    <section class="topbar">
      <h1>Agent 工作编排 / 执行监控</h1>
      <div class="top-actions">
        <el-tag v-if="store.snapshot" type="primary" effect="light" round>
          <span class="pulse" />
          {{ store.snapshot.status === 'running' ? '执行中' : store.snapshot.status }}
        </el-tag>
        <span>2024-05-13 15:21:10</span>
        <el-button text circle>⟳</el-button>
      </div>
    </section>

    <section class="input-panel">
      <el-input v-model="projectId" placeholder="project_id" />
      <el-input v-model="errorCode" placeholder="error_code" />
      <el-input v-model="description" placeholder="故障描述" />
      <el-button type="primary" :loading="store.submitting" @click="submitTask">
        运行 Demo
      </el-button>
    </section>

    <TaskHeader v-if="store.snapshot" :task="store.snapshot" />

    <WorkflowTimeline
      :nodes="store.snapshot?.nodes ?? []"
      :runbook-results="store.runbookResults"
      :events="store.events"
    />

    <RootCause :root-cause="store.rootCause" :status="store.snapshot?.status" />
  </main>
</template>

<style scoped>
.dashboard {
  max-width: 1510px;
  margin: 0 auto;
  padding: 18px 24px 28px;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 12px;
}

h1 {
  margin: 0;
  color: #111827;
  font-size: 26px;
  line-height: 1.25;
  font-weight: 720;
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 18px;
  color: #475467;
  font-size: 14px;
}

.pulse {
  display: inline-block;
  width: 8px;
  height: 8px;
  margin-right: 6px;
  border-radius: 50%;
  background: #1677ff;
}

.input-panel {
  display: grid;
  grid-template-columns: 220px 180px minmax(0, 1fr) 118px;
  gap: 12px;
  align-items: center;
  padding: 12px 16px;
  margin-bottom: 14px;
  border: 1px solid #d9e1ec;
  border-radius: 8px;
  background: #fff;
}

.input-panel :deep(.el-button) {
  height: 32px;
  font-weight: 650;
}

@media (max-width: 860px) {
  .dashboard {
    padding: 18px;
  }

  .topbar,
  .top-actions {
    align-items: flex-start;
    flex-direction: column;
  }

  .input-panel {
    grid-template-columns: 1fr;
  }
}
</style>
