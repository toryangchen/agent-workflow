import { createRouter, createWebHistory } from 'vue-router'
import AgentDashboard from '../views/agent-dashboard/index.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [{ path: '/', component: AgentDashboard }],
})

export default router

