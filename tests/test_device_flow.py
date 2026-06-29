"""Unit tests for OAuth device-flow helpers (device_flow.py)."""

from __future__ import annotations

import asyncio
from typing import Any, List

import pytest

from .conftest import load_module

device_flow = load_module("device_flow")


class _PollResponse:
    def __init__(self, status: int, body: Any):
        self.status = status
        self._body = body

    async def __aenter__(self) -> "_PollResponse":
        return self

    async def __aexit__(self, *exc) -> bool:
        return False

    async def json(self, content_type=None) -> Any:
        return self._body


class _PollSession:
    """Replays a queue of responses for ``session.post`` calls."""

    def __init__(self, responses: List[_PollResponse]):
        self._responses = list(responses)
        self.calls = 0

    def post(self, url, **kwargs):
        self.calls += 1
        return self._responses.pop(0)


async def _poll(session: _PollSession):
    return await device_flow.poll_for_tokens(
        session,
        client_id="cid",
        device_code="dc",
        code_verifier="cv",
        interval=0,
        timeout=60,
    )


def test_safe_error_prefers_description():
    msg = device_flow._safe_error(400, {"error": "invalid_grant", "error_description": "bad"})
    assert "bad" in msg
    assert "400" in msg


def test_safe_error_falls_back_to_error_code():
    msg = device_flow._safe_error(400, {"error": "authorization_pending"})
    assert "authorization_pending" in msg


def test_safe_error_never_leaks_tokens():
    # A (hypothetical) body containing a token must not be echoed verbatim.
    body = {"access_token": "SECRET-TOKEN", "error": "invalid_grant"}
    msg = device_flow._safe_error(400, body)
    assert "SECRET-TOKEN" not in msg


def test_safe_error_handles_non_dict():
    assert "non-JSON" in device_flow._safe_error(500, "<html>oops</html>")


def test_poll_retries_transient_500(monkeypatch):
    """A transient BMW 500 must not abort the flow; polling continues to success."""

    monkeypatch.setattr(device_flow.asyncio, "sleep", _no_sleep)
    session = _PollSession(
        [
            _PollResponse(500, {"error": "internal_error", "error_description": "oops"}),
            _PollResponse(500, None),  # non-JSON-ish body, still transient
            _PollResponse(200, {"access_token": "ok"}),
        ]
    )
    result = asyncio.run(_poll(session))
    assert result == {"access_token": "ok"}
    assert session.calls == 3


def test_poll_retries_network_error(monkeypatch):
    """A transient network error during the POST is retried, not fatal."""

    monkeypatch.setattr(device_flow.asyncio, "sleep", _no_sleep)
    session = _PollSession(
        [
            _RaisingResponse(device_flow.aiohttp.ClientError("boom")),
            _PollResponse(200, {"access_token": "ok"}),
        ]
    )
    result = asyncio.run(_poll(session))
    assert result == {"access_token": "ok"}


def test_poll_gives_up_after_persistent_500(monkeypatch):
    """Persistent server errors eventually surface as a CardataAuthError."""

    monkeypatch.setattr(device_flow.asyncio, "sleep", _no_sleep)
    session = _PollSession([_PollResponse(503, {"error": "down"}) for _ in range(20)])
    with pytest.raises(device_flow.CardataAuthError):
        asyncio.run(_poll(session))


def test_poll_fatal_error_not_retried(monkeypatch):
    """A 4xx auth error (e.g. access_denied) fails immediately."""

    monkeypatch.setattr(device_flow.asyncio, "sleep", _no_sleep)
    session = _PollSession([_PollResponse(400, {"error": "access_denied"})])
    with pytest.raises(device_flow.CardataAuthError):
        asyncio.run(_poll(session))
    assert session.calls == 1


async def _no_sleep(*_args, **_kwargs):
    return None


class _RaisingResponse:
    def __init__(self, exc: Exception):
        self._exc = exc

    def __enter__(self):  # pragma: no cover - not used as sync cm
        raise self._exc

    async def __aenter__(self):
        raise self._exc

    async def __aexit__(self, *exc) -> bool:
        return False
