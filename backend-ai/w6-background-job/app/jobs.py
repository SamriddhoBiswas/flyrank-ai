"""Job status store in Redis — source of truth for the status endpoint."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from redis import Redis

JOB_KEY = "job:{job_id}"
IDEMPOTENCY_KEY = "idempotency:{key}"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_job(
    redis: Redis,
    job_id: str,
    payload: dict[str, Any],
    idempotency_key: str | None = None,
) -> dict:
    record = {
        "id": job_id,
        "status": "queued",
        "payload": payload,
        "result": None,
        "error": None,
        "attempts": 0,
        "idempotency_key": idempotency_key,
        "created_at": _now(),
        "updated_at": _now(),
    }
    redis.set(JOB_KEY.format(job_id=job_id), json.dumps(record))
    if idempotency_key:
        redis.set(IDEMPOTENCY_KEY.format(key=idempotency_key), job_id, ex=86400)
    return record


def get_job_id_for_idempotency(redis: Redis, key: str) -> str | None:
    value = redis.get(IDEMPOTENCY_KEY.format(key=key))
    return value.decode() if value else None


def get_job(redis: Redis, job_id: str) -> dict | None:
    raw = redis.get(JOB_KEY.format(job_id=job_id))
    if not raw:
        return None
    return json.loads(raw)


def update_job(redis: Redis, job_id: str, **fields: Any) -> dict | None:
    record = get_job(redis, job_id)
    if not record:
        return None
    record.update(fields)
    record["updated_at"] = _now()
    redis.set(JOB_KEY.format(job_id=job_id), json.dumps(record))
    return record
