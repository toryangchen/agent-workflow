from __future__ import annotations

async def collect_feisha_logs(project_id: str) -> list[dict[str, str]]:
    return [
        {
            "level": "ERROR",
            "service": project_id,
            "message": "Redis timeout while borrowing connection from pool",
        },
        {
            "level": "ERROR",
            "service": project_id,
            "message": "JAVA_HEAP_OOM observed after Redis timeout spike",
        },
        {
            "level": "WARN",
            "service": project_id,
            "message": "Redis timeout on cache read operation",
        },
    ]

