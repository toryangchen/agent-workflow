import type { TaskSnapshot } from '../types/agent'

export async function createAgentTask(userInput: string): Promise<{ task_id: string; status: string }> {
  const response = await fetch('/api/agent/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_input: userInput }),
  })
  if (!response.ok) throw new Error(await response.text())
  return response.json()
}

export async function fetchTaskSnapshot(taskId: string): Promise<TaskSnapshot> {
  const response = await fetch(`/api/agent/tasks/${taskId}`, {
    method: 'POST',
  })
  if (!response.ok) throw new Error(await response.text())
  return response.json()
}
