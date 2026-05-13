import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { createAgentTask, fetchTaskSnapshot } from '../api/agent'
import type { AgentEvent, RunbookResult, TaskSnapshot } from '../types/agent'

export const useAgentStore = defineStore('agent', () => {
  const snapshot = ref<TaskSnapshot | null>(null)
  const events = ref<AgentEvent[]>([])
  const submitting = ref(false)
  const eventSource = ref<EventSource | null>(null)

  const runbookResults = computed(() => snapshot.value?.runbook_results ?? [])
  const rootCause = computed(() => snapshot.value?.root_cause ?? null)

  async function submit(userInput: string) {
    submitting.value = true
    closeEvents()
    try {
      const created = await createAgentTask(userInput)
      snapshot.value = await fetchTaskSnapshot(created.task_id)
      connectEvents(created.task_id)
    } finally {
      submitting.value = false
    }
  }

  async function refresh(taskId: string) {
    snapshot.value = await fetchTaskSnapshot(taskId)
  }

  function connectEvents(taskId: string) {
    eventSource.value = new EventSource(`/api/agent/tasks/${taskId}/events`)
    const names = [
      'task_started',
      'node_started',
      'node_finished',
      'sub_node_started',
      'sub_node_finished',
      'log',
      'task_completed',
      'task_failed',
    ]
    names.forEach((name) => {
      eventSource.value?.addEventListener(name, (message) => {
        const event = JSON.parse((message as MessageEvent).data) as AgentEvent
        applyEvent(event)
      })
    })
  }

  function closeEvents() {
    eventSource.value?.close()
    eventSource.value = null
    events.value = []
  }

  function applyEvent(event: AgentEvent) {
    events.value.push(event)
    const current = snapshot.value
    if (!current) return
    if (event.type === 'node_started' && event.node_id) {
      current.nodes = current.nodes.map((node) =>
        node.node_id === event.node_id ? { ...node, status: 'running' } : node,
      )
    }
    if (event.type === 'node_finished' && event.node_id) {
      current.nodes = current.nodes.map((node) =>
        node.node_id === event.node_id ? { ...node, status: 'success' } : node,
      )
      if (event.node_id === 'task_init') {
        current.project_id = event.payload.project_id as string
        current.error_code = event.payload.error_code as string
      }
      if (event.node_id === 'common_data') {
        current.context = event.payload.context as unknown as TaskSnapshot['context']
      }
      if (event.node_id === 'root_cause') {
        current.root_cause = event.payload as unknown as TaskSnapshot['root_cause']
      }
    }
    if (event.type === 'sub_node_finished') {
      const result = event.payload as unknown as RunbookResult
      current.runbook_results = [
        ...current.runbook_results.filter((item) => item.runbook_id !== result.runbook_id),
        result,
      ]
    }
    if (event.type === 'task_completed') current.status = 'success'
    if (event.type === 'task_failed') {
      current.status = 'failed'
      current.error_message = event.message
      current.nodes = current.nodes.map((node) =>
        node.status === 'running' ? { ...node, status: 'failed' } : node,
      )
    }
  }

  return {
    snapshot,
    events,
    submitting,
    runbookResults,
    rootCause,
    submit,
    refresh,
    closeEvents,
  }
})
