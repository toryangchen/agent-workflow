<script setup lang="ts">
import type { RootCause } from '../../types/agent'

defineProps<{
  rootCause: RootCause | null
  status?: string
}>()
</script>

<template>
  <section class="panel">
    <header>
      <h2>根因分析结果（{{ rootCause ? '已生成' : '待生成' }}）</h2>
    </header>

    <div class="result-grid">
      <div class="summary-cell">
        <div v-if="!rootCause" class="empty">
          <div class="doc-icon">▤</div>
          <p>根因分析完成后将在此展示</p>
        </div>
        <p v-else class="summary">{{ rootCause.summary }}</p>
      </div>

      <div class="kv">
        <span>根因</span>
        <strong>{{ rootCause ? 'Redis 连接池耗尽' : '--' }}</strong>
        <span>建议</span>
        <strong>{{ rootCause?.suggestions?.[0] ?? '--' }}</strong>
      </div>

      <div class="kv">
        <span>可能原因</span>
        <strong>{{ rootCause ? '连接释放异常 / 最近发布变更' : '--' }}</strong>
        <span>证据</span>
        <strong>{{ rootCause?.evidence?.[0] ?? '--' }}</strong>
      </div>

      <div class="action">
        <span>操作</span>
        <el-button type="primary">拉起工单</el-button>
      </div>
    </div>
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
  padding: 18px 24px 0;
}

h2 {
  margin: 0;
  color: #111827;
  font-size: 18px;
}

.result-grid {
  display: grid;
  grid-template-columns: 1.15fr 0.75fr 1.05fr 0.3fr;
  gap: 28px;
  align-items: start;
  padding: 18px 24px 28px;
}

.summary-cell {
  min-height: 116px;
}

.empty {
  display: grid;
  gap: 10px;
  justify-items: center;
  color: #667085;
  text-align: center;
}

.doc-icon {
  display: grid;
  width: 70px;
  height: 70px;
  place-items: center;
  color: #a5afbf;
  font-size: 34px;
  border: 1px solid #dbe3ee;
  border-radius: 50%;
}

.summary {
  margin: 0;
  color: #1f2937;
  font-size: 15px;
  line-height: 1.8;
}

.kv {
  display: grid;
  gap: 10px;
  color: #4b5563;
  font-size: 14px;
}

.kv strong {
  min-height: 24px;
  color: #111827;
  font-size: 14px;
  font-weight: 500;
  line-height: 1.7;
}

.action {
  display: grid;
  gap: 22px;
  min-height: 106px;
  padding-left: 26px;
  border-left: 1px solid #e5eaf2;
}

.action span {
  font-weight: 700;
}

@media (max-width: 960px) {
  .result-grid {
    grid-template-columns: 1fr;
  }

  .action {
    padding-left: 0;
    border-left: 0;
  }
}
</style>
