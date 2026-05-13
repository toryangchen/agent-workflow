from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.schemas.task_schema import TaskCreateRequest, TaskCreateResponse, TaskSnapshot
from app.services.sse_manager import SSEManager


router = APIRouter(prefix="/api/agent/tasks", tags=["agent-tasks"])


def get_orchestrator(request: Request):
    return request.app.state.orchestrator


def get_task_repository(request: Request):
    return request.app.state.task_repository


def get_sse_manager(request: Request) -> SSEManager:
    return request.app.state.sse_manager


@router.post("", response_model=TaskCreateResponse)
async def create_task(payload: TaskCreateRequest, request: Request):
    orchestrator = get_orchestrator(request)
    task_id = await orchestrator.create_task(payload.user_input)
    return TaskCreateResponse(task_id=task_id, status="running")


@router.post("/{task_id}", response_model=TaskSnapshot)
async def get_task(task_id: str, request: Request):
    task = get_task_repository(request).get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    return task


@router.post("/{task_id}/events")
async def stream_events(task_id: str, request: Request):
    task = get_task_repository(request).get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    sse_manager = get_sse_manager(request)

    async def event_generator():
        async for event in sse_manager.subscribe(task_id):
            yield sse_manager.format_sse(event)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
