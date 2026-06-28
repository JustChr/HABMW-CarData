"""Unit tests for OAuth device-flow helpers (device_flow.py)."""

from __future__ import annotations

from .conftest import load_module

device_flow = load_module("device_flow")


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
