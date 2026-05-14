# Agent Workflow 故障诊断平台

一个 AI Agent + Workflow + Runbook + Script Runtime 的故障诊断平台 MVP。

用户输入自然语言故障描述后，后端通过 OpenAI 兼容接口提取 `project_id` 和 `error_code`，根据错误码匹配多个 Runbook，并通过 LangGraph 编排通用数据采集、并行脚本执行和根因总结生成。前端通过 SSE 实时展示 Timeline、Runbook 状态和 Root Cause Summary。

## 架构

```text
Frontend(Vue3)
  -> HTTP + SSE
FastAPI API Layer
  -> Agent Orchestrator
  -> LangGraph Workflow
  -> Context Manager
  -> Runbook Engine
  -> Script Runtime
  -> Root Cause Analyzer(LLM)
  -> SSE Stream Manager
```

## 目录

```text
backend/
  app/
    api/                  FastAPI 路由
    collectors/           Mock 数据采集器
    repositories/         内存任务/事件仓库
    runbook_engine/       YAML 加载、映射、脚本执行
    services/             Orchestrator、SSE、LLM、Root Cause
    workflow/             LangGraph 状态和节点
  runbooks/               内置 Runbook
frontend/
  src/
    views/agent-dashboard 单页诊断 Dashboard
    stores/               Pinia 状态
    api/                  HTTP API
```

## 后端启动

```bash
cd backend
python -m pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

`.env` 示例：

```env
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://your-openai-compatible-endpoint/v1
LLM_MODEL=your-model-name
APP_ENV=development
```

开发环境下如果没有配置 `LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL`，后端会自动启用 mock LLM：

- 第一节点从输入中用规则解析 `project_id` 和 `error_code`
- 最后一节点生成固定但包含 Runbook 证据的中文根因分析
- 因此无需大模型 API key 也可以跑完整 Demo

如果使用官方 OpenAI：

```env
LLM_API_KEY=your-openai-api-key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-5.2
```

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173`。

## API 示例

创建任务：

```bash
curl -X POST http://localhost:8000/api/agent/tasks \
  -H 'Content-Type: application/json' \
  -d '{"user_input":"payment-service-prod 最近 Redis timeout 很严重，错误码 JAVA_HEAP_OOM"}'
```

查询任务：

```bash
curl -X POST http://localhost:8000/api/agent/tasks/{task_id}
```

监听事件：

```bash
curl -N -X POST http://localhost:8000/api/agent/tasks/{task_id}/events
```

## Runbook 编写

每个 Runbook 是一个独立目录：

```text
runbooks/redis_timeout_check/
  runbook.yaml
  script.py
```

`runbook.yaml`：

```yaml
id: redis_timeout_check
name: Redis Timeout 检查
description: 检查 Redis timeout 是否异常
requires:
  - feisha_logs
  - monitor_metrics
timeout: 30
tags:
  - redis
```

`script.py` 中可以访问：

- `context`：通用上下文数据
- `result`：脚本写入的结构化结果
- `http`：平台注入的受控 HTTP Client，支持 `get/post`，自动应用 host 白名单和 timeout

示例：

```python
logs = context.get("feisha_logs", [])
timeout_count = 0

for log in logs:
    if "Redis timeout" in str(log):
        timeout_count += 1

result["status"] = "success"
result["summary"] = f"发现 Redis timeout {timeout_count} 次"
result["evidence"] = [f"Redis timeout 次数：{timeout_count}"]
result["suggestion"] = "建议检查 Redis 连接池"
```

脚本内网络请求示例：

```python
response = http.get("https://monitor-api.internal/api/status", timeout=2)
payload = response.json()

result["summary"] = f"监控接口状态：{payload.get('status')}"
result["evidence"] = [f"HTTP status：{response.status_code}"]
```

HTTP 访问控制配置：

```env
RUNBOOK_HTTP_ALLOWED_HOSTS=httpbin.org,monitor-api.internal,cmdb.internal,log-api.internal
RUNBOOK_HTTP_TIMEOUT_SECONDS=3
```

如果目标 host 不在白名单中，Runbook 会执行失败并把错误写入 `RunbookResult.error`。生产环境不建议配置 `*`，除非是在完全隔离的测试环境。

错误码映射在 `backend/runbooks/error_code_mapping.yaml`。

## AgentContext

每个任务会创建一个独立的 `AgentContext`，贯穿完整 workflow 周期：

```text
task_id
user_input
project_id
error_code
project_info
lld_topology
feisha_logs
monitor_metrics
release_info
runbooks
runbook_results
root_cause
scratchpad
```

第二节点会把 LLD、日志、监控、发布等数据写入 `AgentContext`。第三节点执行 Runbook 时，会把 `AgentContext.runtime_view()` 注入脚本的 `context` 变量；脚本通过写 `result` 字典把结果回传给 Python runtime。

## 测试

后端：

```bash
cd backend
pytest -q
```

前端：

```bash
cd frontend
npm run build
```

## MVP 限制

- 任务、节点、事件都保存在内存，后端重启后丢失。
- Runbook script 被视为仓库内可信脚本，不支持执行用户上传代码。
- `APP_ENV=development` 且 LLM 配置缺失时会使用 mock LLM，方便本地完整演示。
