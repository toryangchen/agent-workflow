metrics = context.get("monitor_metrics", {})
release_info = context.get("release_info", {})

heap_usage = int(metrics.get("jvm_heap_usage_percent", 0))
thread_count = int(metrics.get("jvm_thread_count", 0))

result["status"] = "success" if heap_usage < 95 else "warning"
result["summary"] = f"JVM 堆内存使用率 {heap_usage}%，线程数 {thread_count}"
result["evidence"] = [
    f"JVM heap usage：{heap_usage}%",
    f"JVM thread count：{thread_count}",
    f"最近发布：{release_info.get('latest_release', '-')}",
]
result["suggestion"] = "建议结合 heap dump 检查对象增长，并确认最近发布是否引入连接泄漏"

