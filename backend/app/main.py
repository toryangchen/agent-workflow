from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.agent_task_api import router as agent_task_router
from app.core.config import settings
from app.repositories.context_repository import AgentContextRepository
from app.repositories.event_repository import EventRepository
from app.repositories.task_repository import TaskRepository
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.llm_service import LLMService
from app.services.sse_manager import SSEManager


def create_app() -> FastAPI:
    app = FastAPI(title="Agent Workflow 故障诊断平台")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    task_repository = TaskRepository()
    context_repository = AgentContextRepository()
    sse_manager = SSEManager(EventRepository())
    llm_service = LLMService()

    app.state.task_repository = task_repository
    app.state.sse_manager = sse_manager
    app.state.orchestrator = AgentOrchestrator(
        task_repository=task_repository,
        sse_manager=sse_manager,
        llm_service=llm_service,
        context_repository=context_repository,
    )
    app.include_router(agent_task_router)
    return app


app = create_app()
