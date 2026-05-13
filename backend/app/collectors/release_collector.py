async def collect_release_info(project_id: str) -> dict:
    return {
        "project_id": project_id,
        "latest_release": "2026.05.13-rc1",
        "released_at": "2026-05-13T09:10:00+08:00",
        "changes": ["调整 Redis 客户端连接池配置", "升级 payment retry 逻辑"],
    }

