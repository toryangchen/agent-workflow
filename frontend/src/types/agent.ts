export type NodeStatus = 'pending' | 'running' | 'success' | 'failed'

export interface WorkflowNode {
  node_id: string
  name: string
  status: NodeStatus
}

export interface RunbookResult {
  runbook_id: string
  name: string
  status: string
  summary: string
  evidence: string[]
  suggestion: string
  error?: string | null
  elapsed_ms: number
}

export interface RootCause {
  summary: string
  evidence: string[]
  suggestions: string[]
}

export interface AgentContext {
  task_id: string
  user_input: string
  project_id?: string | null
  error_code?: string | null
  project_info: Record<string, unknown>
  lld_topology: Record<string, unknown>
  feisha_logs: unknown[]
  monitor_metrics: Record<string, unknown>
  release_info: Record<string, unknown>
  scratchpad: Record<string, unknown>
}

export interface TaskSnapshot {
  task_id: string
  user_input: string
  status: string
  project_id?: string | null
  error_code?: string | null
  nodes: WorkflowNode[]
  runbook_results: RunbookResult[]
  root_cause?: RootCause | null
  context?: AgentContext | null
  error_message?: string | null
}

export interface AgentEvent {
  event_id: string
  task_id: string
  type: string
  timestamp: string
  node_id?: string | null
  runbook_id?: string | null
  message: string
  payload: Record<string, unknown>
}
