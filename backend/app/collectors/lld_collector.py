async def collect_lld_topology(project_id: str) -> dict:
    return {
        "project_id": project_id,
        "dependencies": ["redis-cluster-prod", "mysql-payment-prod", "mq-payment-prod"],
        "owners": ["payment-platform"],
    }

