logs = context.get("feisha_logs", [])
metrics = context.get("monitor_metrics", {})

timeout_count = 0
for log in logs:
    if "Redis timeout" in str(log):
        timeout_count += 1

metric_count = int(metrics.get("redis_timeout_count", 0))
display_count = timeout_count if timeout_count else metric_count

result["status"] = "success"
result["summary"] = f"发现 Redis timeout {display_count} 次"
result["evidence"] = [
    f"日志命中 Redis timeout 次数：{timeout_count}",
    f"监控 Redis timeout 次数：{metric_count}",
    f"Redis 连接池使用：{metrics.get('redis_pool_active', '-')}/{metrics.get('redis_pool_max', '-')}",
]
result["suggestion"] = "建议检查 Redis 连接池释放逻辑和连接池上限配置"

