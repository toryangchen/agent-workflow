from app.main import create_app


def test_agent_api_exposes_only_post_methods():
    schema = create_app().openapi()

    assert set(schema["paths"]["/api/agent/tasks"].keys()) == {"post"}
    assert set(schema["paths"]["/api/agent/tasks/{task_id}"].keys()) == {"post"}
    assert set(schema["paths"]["/api/agent/tasks/{task_id}/events"].keys()) == {"post"}
