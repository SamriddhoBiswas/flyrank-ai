"""Alerts when a job permanently fails."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

from app.config import ALERT_LOG_PATH, ALERT_WEBHOOK_URL


def alert_job_failed(job_id: str, error: str, attempts: int) -> None:
    message = {
        "event": "job_failed",
        "job_id": job_id,
        "error": error,
        "attempts": attempts,
        "at": datetime.now(timezone.utc).isoformat(),
    }

    path = Path(ALERT_LOG_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(message) + "\n")
    print(f"[ALERT] job {job_id} failed after {attempts} attempts: {error}")

    if ALERT_WEBHOOK_URL:
        try:
            httpx.post(ALERT_WEBHOOK_URL, json=message, timeout=5)
        except Exception as exc:
            print(f"[ALERT] webhook failed: {exc}")
