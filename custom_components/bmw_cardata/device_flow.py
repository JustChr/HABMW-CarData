"""Helpers for the MyBMW Device Code OAuth 2.0 flow."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, Optional

import aiohttp

from .const import DEVICE_CODE_URL, TOKEN_URL


class CardataAuthError(Exception):
    """Raised when the BMW OAuth service rejects a request."""


# Network timeout for individual OAuth requests. A single poll/refresh must never
# hang the event loop indefinitely.
HTTP_TIMEOUT = aiohttp.ClientTimeout(total=30)


def _safe_error(status: int, data: Any) -> str:
    """Build an error string without leaking tokens from the response body.

    Successful (200) responses carry access/refresh/id tokens. Only the OAuth
    error fields are safe to surface in exceptions/logs.
    """

    if isinstance(data, dict):
        detail = data.get("error_description") or data.get("error") or "unknown_error"
    else:
        detail = "non-JSON response"
    return f"{status}: {detail}"


async def request_device_code(
    session: aiohttp.ClientSession,
    *,
    client_id: str,
    scope: str,
    code_challenge: str,
    code_challenge_method: str = "S256",
) -> Dict[str, Any]:
    """Request a device & user code pair from BMW."""

    data = {
        "client_id": client_id,
        "scope": scope,
        "response_type": "device_code",
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method,
    }
    async with session.post(DEVICE_CODE_URL, data=data, timeout=HTTP_TIMEOUT) as resp:
        payload = await resp.json(content_type=None)
        if resp.status != 200:
            raise CardataAuthError(
                f"Device code request failed ({_safe_error(resp.status, payload)})"
            )
        return payload


async def poll_for_tokens(
    session: aiohttp.ClientSession,
    *,
    client_id: str,
    device_code: str,
    code_verifier: str,
    interval: int,
    timeout: int = 900,
    token_url: str = TOKEN_URL,
) -> Dict[str, Any]:
    """Poll the token endpoint until tokens are issued or timeout elapsed."""

    start = time.monotonic()
    payload = {
        "client_id": client_id,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "device_code": device_code,
        "code_verifier": code_verifier,
    }

    while True:
        if time.monotonic() - start > timeout:
            raise CardataAuthError("Timed out waiting for device authorization")

        async with session.post(token_url, data=payload, timeout=HTTP_TIMEOUT) as resp:
            data = await resp.json(content_type=None)
            if resp.status == 200:
                return data

            error = data.get("error") if isinstance(data, dict) else None
            if error in {"authorization_pending", "slow_down"}:
                await asyncio.sleep(interval if error == "authorization_pending" else interval + 5)
                continue

            raise CardataAuthError(
                f"Token polling failed ({_safe_error(resp.status, data)})"
            )


async def refresh_tokens(
    session: aiohttp.ClientSession,
    *,
    client_id: str,
    refresh_token: str,
    scope: Optional[str] = None,
    token_url: str = TOKEN_URL,
) -> Dict[str, Any]:
    """Refresh access/ID tokens using the stored refresh token."""

    payload = {
        "client_id": client_id,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    if scope:
        payload["scope"] = scope

    async with session.post(token_url, data=payload, timeout=HTTP_TIMEOUT) as resp:
        data = await resp.json(content_type=None)
        if resp.status != 200:
            raise CardataAuthError(
                f"Token refresh failed ({_safe_error(resp.status, data)})"
            )
        return data
