<script setup lang="ts">
import { computed } from 'vue'
import type { AgentEvent, RunbookResult, WorkflowNode } from '../../types/agent'

const props = defineProps<{
  nodes: WorkflowNode[]
  runbookResults: RunbookResult[]
  events: AgentEvent[]
}>()

const descriptions: Record<string, string> = {
  task_init: '参数校验、加载 Runbooks、准备执行环境',
  common_data: '获取项目通用数据（LLD、日志、监控等）',
  runbook_execute: '并行执行多个 Runbooks',
  root_cause: '汇总分析结果，生成根因与建议',
}

const commonStepNames = [
  ['lld_topology', 'LLD 信息获取'],
  ['feisha_logs', '飞盟日志获取'],
  ['monitor_metrics', '监控指标获取'],
  ['release_info', '发布记录获取'],
]

const commonSubSteps = computed(() => {
  return commonStepNames.map(([stepId, name]) => subStepFromEvents('common_data', stepId, name))
})

const runbookSubSteps = computed(() =>
  props.runbookResults.map((result) => ({
    id: result.runbook_id,
    name: result.name,
    summary: result.summary,
    status: result.status === 'failed' ? 'failed' : 'success',
    duration: formatMilliseconds(result.elapsed_ms),
  })),
)

function statusText(status: string) {
  return status === 'success' ? '成功' : status === 'running' ? '执行中' : status === 'failed' ? '失败' : '等待中'
}

function subStepFromEvents(nodeId: string, stepId: string, fallbackName: string) {
  const started = props.events.find(
    (event) =>
      event.node_id === nodeId &&
      event.type === 'sub_node_started' &&
      event.payload.step_id === stepId,
  )
  const finished = props.events.find(
    (event) =>
      event.node_id === nodeId &&
      event.type === 'sub_node_finished' &&
      event.payload.step_id === stepId,
  )
  return {
    id: stepId,
    name: (finished?.payload.name as string) || (started?.payload.name as string) || fallbackName,
    status: finished ? 'success' : started ? 'running' : 'pending',
    duration: started && finished ? durationBetween(started.timestamp, finished.timestamp) : '--',
    summary: '',
  }
}

function eventFor(nodeId: string, type: string) {
  return props.events.find((event) => event.node_id === nodeId && event.type === type)
}

function durationFor(node: WorkflowNode) {
  const started = eventFor(node.node_id, 'node_started')
  const finished = eventFor(node.node_id, 'node_finished')
  if (!started) return '--'
  return durationBetween(started.timestamp, finished?.timestamp ?? new Date().toISOString())
}

function finishedAt(node: WorkflowNode) {
  const event = eventFor(node.node_id, 'node_finished') ?? eventFor(node.node_id, 'node_started')
  if (!event) return '--:--:--'
  return new Date(event.timestamp).toLocaleTimeString('zh-CN', { hour12: false })
}

function durationBetween(start: string, end: string) {
  return formatMilliseconds(Math.max(0, new Date(end).getTime() - new Date(start).getTime()))
}

function formatMilliseconds(ms: number) {
  const totalSeconds = Math.max(0, Math.round(ms / 1000))
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60
  return [hours, minutes, seconds].map((item) => String(item).padStart(2, '0')).join(':')
}
</script>

<template>
  <section class="panel">
    <header>
      <h2>执行流程</h2>
    </header>

    <div v-if="!nodes.length" class="empty">点击“运行 Demo”后展示执行流程</div>

    <ol v-else class="timeline">
      <li v-for="(node, index) in nodes" :key="node.node_id" :class="{ expanded: node.node_id === 'common_data' && node.status !== 'pending' }">
        <div class="rail">
          <span class="step">{{ index + 1 }}</span>
          <span class="status-ring" :class="node.status" />
        </div>

        <div class="node-body">
          <div class="node-head">
            <div>
              <strong>{{ node.name }}</strong>
              <el-tag size="small" :type="node.status === 'failed' ? 'danger' : node.status === 'success' ? 'success' : node.status === 'running' ? 'primary' : 'info'">
                {{ statusText(node.status) }}
              </el-tag>
              <p>{{ descriptions[node.node_id] }}</p>
            </div>
            <div class="node-meta">
              <span>{{ durationFor(node) }}</span>
              <span>{{ finishedAt(node) }}</span>
              <span class="chevron">⌄</span>
            </div>
          </div>

          <div v-if="node.node_id === 'common_data' && node.status !== 'pending'" class="sub-panel">
            <div v-for="item in commonSubSteps" :key="item.id" class="sub-row">
              <span class="sub-dot" :class="item.status" />
              <span>{{ item.name }}</span>
              <span class="sub-status">{{ statusText(item.status) }}</span>
              <span>{{ item.duration }}</span>
            </div>
          </div>

          <div v-if="node.node_id === 'runbook_execute' && runbookSubSteps.length" class="sub-panel">
            <div v-for="result in runbookSubSteps" :key="result.id" class="sub-row runbook-row">
              <span class="sub-dot" :class="result.status" />
              <span>
                <strong>{{ result.name }}</strong>
                <small>{{ result.summary }}</small>
              </span>
              <span class="sub-status">{{ statusText(result.status) }}</span>
              <span>{{ result.duration }}</span>
            </div>
          </div>
        </div>
      </li>
    </ol>

    <footer>
      <span><i class="legend success" />成功</span>
      <span><i class="legend running" />执行中</span>
      <span><i class="legend pending" />等待中</span>
      <span><i class="legend failed" />失败</span>
    </footer>
  </section>
</template>

<style scoped>
.panel {
  margin-top: 14px;
  border: 1px solid #d9e1ec;
  border-radius: 8px;
  background: #fff;
}

header {
  padding: 18px 24px 8px;
}

h2 {
  margin: 0;
  color: #111827;
  font-size: 18px;
}

.empty {
  margin: 18px 24px 24px;
  padding: 28px;
  color: #667085;
  text-align: center;
  border: 1px dashed #d8dee9;
  border-radius: 8px;
}

.timeline {
  margin: 0;
  padding: 0;
  list-style: none;
}

li {
  display: grid;
  grid-template-columns: 88px minmax(0, 1fr);
  min-height: 82px;
  border-bottom: 1px solid #e8edf5;
}

.rail {
  position: relative;
  display: flex;
  gap: 28px;
  justify-content: center;
  padding-top: 26px;
}

.rail::after {
  position: absolute;
  top: 54px;
  bottom: -28px;
  left: 44px;
  width: 1px;
  content: '';
  background: #cfd8e5;
}

li:last-child .rail::after {
  display: none;
}

.step {
  display: grid;
  width: 28px;
  height: 28px;
  place-items: center;
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  border-radius: 50%;
  background: #8b95a5;
}

li:has(.status-ring.success) .step,
li:has(.status-ring.running) .step {
  background: #1677ff;
}

.status-ring {
  width: 24px;
  height: 24px;
  border: 3px solid #9aa4b2;
  border-radius: 50%;
}

.status-ring.success {
  position: relative;
  border-color: #238a4b;
  background: #238a4b;
}

.status-ring.success::after {
  position: absolute;
  top: 2px;
  left: 6px;
  width: 6px;
  height: 11px;
  content: '';
  border: solid #fff;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.status-ring.running {
  border-color: #1677ff;
  border-top-color: transparent;
}

.node-body {
  padding: 22px 32px 20px 0;
}

.node-head {
  display: flex;
  justify-content: space-between;
  gap: 24px;
}

.node-head strong {
  margin-right: 12px;
  color: #111827;
  font-size: 16px;
}

.node-head p {
  margin: 8px 0 0;
  color: #4b5563;
  font-size: 14px;
}

.node-meta {
  display: grid;
  grid-template-columns: 100px 100px 24px;
  gap: 16px;
  align-items: center;
  color: #374151;
  font-size: 14px;
  text-align: right;
}

.sub-panel {
  display: grid;
  gap: 14px;
  margin-top: 18px;
  padding: 18px 22px;
  border: 1px solid #cfe0f5;
  border-radius: 6px;
  background: #f8fbff;
}

.sub-row {
  display: grid;
  grid-template-columns: 16px minmax(0, 1fr) 140px 130px;
  gap: 12px;
  align-items: center;
  color: #344054;
  font-size: 14px;
}

.sub-dot,
.legend {
  width: 10px;
  height: 10px;
  border: 2px solid #98a2b3;
  border-radius: 50%;
}

.sub-dot.success,
.legend.success {
  border-color: #238a4b;
  background: #238a4b;
}

.sub-dot.running,
.legend.running {
  border-color: #1677ff;
}

.sub-dot.failed,
.legend.failed {
  border-color: #ef4444;
}

.sub-status {
  color: #1677ff;
}

.runbook-row small {
  display: block;
  margin-top: 4px;
  color: #667085;
}

footer {
  display: flex;
  gap: 24px;
  padding: 14px 24px;
  color: #344054;
  font-size: 14px;
}

footer span {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

@media (max-width: 860px) {
  li,
  .node-head,
  .sub-row {
    grid-template-columns: 1fr;
  }

  li {
    display: block;
    padding-left: 18px;
  }

  .rail {
    display: none;
  }

  .node-meta {
    grid-template-columns: repeat(3, auto);
    margin-top: 12px;
    text-align: left;
  }
}
</style>
