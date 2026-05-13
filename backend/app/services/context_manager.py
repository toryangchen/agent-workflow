from __future__ import annotations

from typing import Any

from app.collectors.feisha_log_collector import collect_feisha_logs
from app.collectors.lld_collector import collect_lld_topology
from app.collectors.monitor_collector import collect_monitor_metrics
from app.collectors.release_collector import collect_release_info

from app.schemas.context_schema import AgentContext


class ContextManager:
    async def collect(
        self,
        context: AgentContext,
        required_keys: set[str],
    ) -> AgentContext:
        project_id = context.project_id or ""
        if "feisha_logs" in required_keys:
            context.feisha_logs = await collect_feisha_logs(project_id)
        if "monitor_metrics" in required_keys:
            context.monitor_metrics = await collect_monitor_metrics(project_id)
        if "release_info" in required_keys:
            context.release_info = await collect_release_info(project_id)
        if "lld_topology" in required_keys:
            context.lld_topology = await collect_lld_topology(project_id)
        context.project_info = {
            "project_id": project_id,
            "environment": "prod" if project_id.endswith("-prod") else "unknown",
            "owner": "payment-platform",
        }
        return context
