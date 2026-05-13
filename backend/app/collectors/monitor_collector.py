async def collect_monitor_metrics(project_id: str) -> dict:
    return {
        "project_id": project_id,
        "redis_timeout_count": 128,
        "redis_pool_active": 96,
        "redis_pool_max": 100,
        "jvm_heap_usage_percent": 93,
        "jvm_thread_count": 420,
        "request_p95_ms": 1800,
    }

