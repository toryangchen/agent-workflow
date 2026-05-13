logs = context.get("feisha_logs", [])
topology = context.get("lld_topology", {})

error_logs = []
for log in logs:
    if "ERROR" in str(log) or "JAVA_HEAP_OOM" in str(log) or "Redis timeout" in str(log):
        error_logs.append(log)

result["status"] = "success"
result["summary"] = f"发现关键错误日志 {len(error_logs)} 条"
result["evidence"] = [
    f"关键错误日志数量：{len(error_logs)}",
    f"依赖服务：{', '.join(topology.get('dependencies', []))}",
]
result["suggestion"] = "建议优先关联 Redis 依赖、JVM OOM 日志和发布时间线"

