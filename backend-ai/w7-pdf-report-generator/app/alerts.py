from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import httpx

from app.config import ALERT_LOG_PATH


def alert_job_failed(job_id: str, error: str, attempts: int) -> None:
    message = {
        "event": "report_job_failed",
        "job_id": job_id,
        "error": error,
        "attempts": attempts,
        "at": datetime.now(timezone.utc).isoformat(),
    }
    path = Path(ALERT_LOG_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(message) + "\n")
    print(f"[ALERT] report job {job_id} failed: {error}")
