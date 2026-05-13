from pathlib import Path

import pytest

from app.runbook_engine.http_client import RunbookHttpClient
from app.runbook_engine.sandbox import execute_script


class FakeResponse:
    status_code = 200
    headers = {"content-type": "application/json"}
    text = '{"status":"ok","count":3}'

    def json(self):
        return {"status": "ok", "count": 3}


class FakeTransport:
    def __init__(self):
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return FakeResponse()


def test_runbook_http_client_allows_whitelisted_host():
    transport = FakeTransport()
    client = RunbookHttpClient(
        allowed_hosts=["monitor.internal"],
        default_timeout_seconds=2,
        transport=transport,
    )

    response = client.get("https://monitor.internal/api/status")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "count": 3}
    assert transport.calls[0][0] == "GET"
    assert transport.calls[0][2]["timeout"] == 2


def test_runbook_http_client_blocks_non_whitelisted_host():
    client = RunbookHttpClient(
        allowed_hosts=["monitor.internal"],
        default_timeout_seconds=2,
        transport=FakeTransport(),
    )

    with pytest.raises(ValueError, match="not allowed"):
        client.get("https://example.com/api/status")


def test_sandbox_injects_http_client(tmp_path: Path):
    script = tmp_path / "script.py"
    script.write_text(
        "\n".join(
            [
                'response = http.get("https://monitor.internal/api/status")',
                'payload = response.json()',
                'result["summary"] = payload["status"]',
                'result["evidence"] = [str(payload["count"])]',
            ]
        ),
        encoding="utf-8",
    )
    client = RunbookHttpClient(
        allowed_hosts=["monitor.internal"],
        default_timeout_seconds=2,
        transport=FakeTransport(),
    )

    result = execute_script(str(script), context={}, http_client=client)

    assert result["summary"] == "ok"
    assert result["evidence"] == ["3"]
