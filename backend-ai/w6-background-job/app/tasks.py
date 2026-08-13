"""
Background task: simulated slow AI call.

Idempotent: if the job already succeeded, return the stored result
without calling the "AI" again.
"""

from __future__ import annotations

import hashlib
import time

from app.alerts import alert_job_failed
from app.config import AI_CALL_SECONDS, JOB_MAX_RETRIES
from app.jobs import get_job, update_job
from app.queue import get_redis


def _fake_ai_summary(text: str) -> dict:
    """Stand-in for a slow LLM / A6 AI call."""
    time.sleep(AI_CALL_SECONDS)
    words = text.split()
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return {
        "summary": " ".join(words[:20]) + ("…" if len(words) > 20 else ""),
        "word_count": len(words),
        "model": "fake-ai-v1",
        "fingerprint": digest,
    }


def run_ai_job(job_id: str) -> dict:
    redis = get_redis()
    job = get_job(redis, job_id)
    if not job:
        raise ValueError(f"Unknown job {job_id}")

    # Idempotency: already done → no side effects
    if job["status"] == "succeeded" and job.get("result"):
        print(f"[worker] job {job_id} already succeeded — skipping")
        return job["result"]

    attempts = int(job.get("attempts") or 0) + 1
    update_job(redis, job_id, status="running", attempts=attempts, error=None)

    text = (job.get("payload") or {}).get("text") or ""
    if not text.strip():
        error = "payload.text is required"
        update_job(redis, job_id, status="failed", error=error)
        alert_job_failed(job_id, error, attempts)
        raise ValueError(error)

    # Force a retryable failure on first attempt if client asked for it
    force_fail = bool((job.get("payload") or {}).get("force_fail_once"))
    if force_fail and attempts == 1:
        error = "simulated transient AI failure"
        update_job(redis, job_id, status="failed", error=error)
        raise RuntimeError(error)

    try:
        result = _fake_ai_summary(text)
        update_job(redis, job_id, status="succeeded", result=result, error=None)
        print(f"[worker] job {job_id} succeeded on attempt {attempts}")
        return result
    except Exception as exc:
        error = str(exc)
        update_job(redis, job_id, status="failed", error=error)
        if attempts >= JOB_MAX_RETRIES:
            alert_job_failed(job_id, error, attempts)
        raise
