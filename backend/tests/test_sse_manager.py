import asyncio

from app.schemas.event_schema import EventType
from app.services.sse_manager import SSEManager


def test_sse_manager_replays_existing_events_and_streams_new_events():
    async def run():
        manager = SSEManager()
        first = await manager.publish(
            task_id="task-1",
            event_type=EventType.TASK_STARTED,
            message="任务开始",
        )

        stream = manager.subscribe("task-1")
        replayed = await stream.__anext__()

        second = await manager.publish(
            task_id="task-1",
            event_type=EventType.LOG,
            message="采集日志",
        )
        live = await stream.__anext__()
        await stream.aclose()
        return first, replayed, second, live

    first, replayed, second, live = asyncio.run(run())

    assert replayed.event_id == first.event_id
    assert live.event_id == second.event_id
    assert live.message == "采集日志"

