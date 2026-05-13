from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import httpx


class RunbookHttpResponse:
    def __init__(self, response: Any) -> None:
        self.status_code = int(response.status_code)
        self.headers = dict(response.headers)
        self.text = str(response.text)
        self._response = response

    def json(self) -> Any:
        return self._response.json()


class HttpxTransport:
    def request(self, method: str, url: str, **kwargs):
        with httpx.Client(follow_redirects=False) as client:
            return client.request(method, url, **kwargs)


class RunbookHttpClient:
    def __init__(
        self,
        allowed_hosts: list[str] | tuple[str, ...],
        default_timeout_seconds: float,
        transport: Any | None = None,
    ) -> None:
        self.allowed_hosts = {host.lower() for host in allowed_hosts}
        self.default_timeout_seconds = default_timeout_seconds
        self.transport = transport or HttpxTransport()

    def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> RunbookHttpResponse:
        return self.request(
            "GET",
            url,
            headers=headers,
            params=params,
            timeout=timeout,
        )

    def post(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        timeout: float | None = None,
    ) -> RunbookHttpResponse:
        return self.request(
            "POST",
            url,
            headers=headers,
            json=json,
            data=data,
            timeout=timeout,
        )

    def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        **kwargs,
    ) -> RunbookHttpResponse:
        self._check_allowed(url)
        response = self.transport.request(
            method.upper(),
            url,
            headers=headers or {},
            timeout=timeout or self.default_timeout_seconds,
            **kwargs,
        )
        return RunbookHttpResponse(response)

    def _check_allowed(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError(f"Runbook HTTP scheme is not allowed: {parsed.scheme}")
        host = (parsed.hostname or "").lower()
        if not host:
            raise ValueError("Runbook HTTP URL must include a host")
        if "*" in self.allowed_hosts:
            return
        if host not in self.allowed_hosts:
            raise ValueError(f"Runbook HTTP host is not allowed: {host}")
