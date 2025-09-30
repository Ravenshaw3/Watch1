#!/usr/bin/env python3
"""Trigger a media scan and category refresh for Watch1.

This helper logs into the local Watch1 API using the standard development
credentials and invokes the media scan endpoint. It is intended for use in
local development workflows whenever new media files are added or categories
need to be recalculated.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict

import requests


def _env(name: str, default: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    return default


def login(api_url: str, username: str, password: str) -> str:
    """Obtain a JWT access token from the Watch1 backend."""
    response = requests.post(
        f"{api_url}/api/v1/auth/login/access-token",
        json={"username": username, "password": password},
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"Login failed ({response.status_code}): {response.text}"
        )

    data = response.json()
    token = data.get("access_token")
    if not token:
        raise RuntimeError("Login succeeded but no access_token was returned")
    return token


def trigger_scan(api_url: str, token: str, request_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke the media scan endpoint and return the JSON response."""
    response = requests.post(
        f"{api_url}/api/v1/media/scan",
        json=request_payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=120,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"Scan failed ({response.status_code}): {response.text}"
        )
    return response.json()


def main() -> int:
    api_url = _env("WATCH1_API_URL", "http://localhost:8000")
    username = _env("WATCH1_USERNAME", _env("WATCH1_EMAIL", "test@example.com"))
    password = _env("WATCH1_PASSWORD", "testpass123")
    directory = _env("WATCH1_MEDIA_DIRECTORY", "/app/media")

    payload: Dict[str, Any]
    if directory:
        payload = {"directory": directory}
    else:
        payload = {}

    rebuild_flag = os.getenv("WATCH1_RECALCULATE_CATEGORIES")
    if rebuild_flag and rebuild_flag.lower() in {"1", "true", "yes"}:
        payload["recalculate_categories"] = True

    print(f"🔐 Logging in to {api_url} as {username}...")
    token = login(api_url, username, password)
    print("✅ Login successful")

    print("🔄 Triggering media scan and category refresh...")
    response = trigger_scan(api_url, token, payload)

    print("✅ Scan request accepted")
    print("📄 Response:")
    print(response)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"❌ {exc}", file=sys.stderr)
        raise SystemExit(1)
