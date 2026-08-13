"""
Background jobs API.

POST /jobs      → 202 Accepted (enqueue slow AI work)
GET  /jobs/{id} → status + result
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from rq import Retry

from app.config import JOB_MAX_RETRIES
from app.jobs import create_job, get_job, get_job_id_for_idempotency
from app.queue import get_queue, get_redis
from app.tasks import run_ai_job

app = FastAPI(
    title="Background Jobs API",
    description="Accept fast (202), work in the background, report status.",
    version="1.0",
)


class JobCreate(BaseModel):
    text: str = Field(..., min_length=1, description="Text to send to the slow AI call")
    force_fail_once: bool = Field(
        False, description="Simulate a transient failure on the first attempt (for retry demos)"
    )


@app.get("/")
def root():
    return {
        "name": "Background Jobs API",
        "version": "1.0",
        "pattern": "accept fast → worker → status",
        "endpoints": ["/jobs", "/jobs/{job_id}", "/health"],
    }


@app.get("/health")
def health():
    redis = get_redis()
    redis.ping()
    return {"status": "ok"}


@app.post("/jobs", status_code=202)
def enqueue_job(
    body: JobCreate,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    """
    Enqueue a slow AI job and return immediately with 202 Accepted.
    Send the same Idempotency-Key to safely retry the HTTP request.
    """
    redis = get_redis()

    if idempotency_key:
        existing_id = get_job_id_for_idempotency(redis, idempotency_key)
        if existing_id:
            existing = get_job(redis, existing_id)
            if existing:
                return JSONResponse(
                    status_code=202,
                    content={
                        "job_id": existing_id,
                        "status": existing["status"],
                        "status_url": f"/jobs/{existing_id}",
                        "idempotent_replay": True,
                    },
                )

    job_id = str(uuid.uuid4())
    payload: dict[str, Any] = {
        "text": body.text,
        "force_fail_once": body.force_fail_once,
    }
    create_job(redis, job_id, payload, idempotency_key=idempotency_key)

    queue = get_queue(redis)
    queue.enqueue(
        run_ai_job,
        job_id,
        job_id=job_id,
        retry=Retry(max=JOB_MAX_RETRIES, interval=[2, 4, 8]),
        failure_ttl=86400,
        result_ttl=86400,
    )

    return {
        "job_id": job_id,
        "status": "queued",
        "status_url": f"/jobs/{job_id}",
        "message": "Job accepted. Poll status_url for the result.",
    }


@app.get("/jobs/{job_id}")
def job_status(job_id: str):
    """Report queued / running / succeeded / failed (+ result or error)."""
    job = get_job(get_redis(), job_id)
    if not job:
        return JSONResponse(status_code=404, content={"error": f"Job {job_id} not found"})

    return {
        "job_id": job["id"],
        "status": job["status"],
        "attempts": job.get("attempts", 0),
        "result": job.get("result"),
        "error": job.get("error"),
        "created_at": job.get("created_at"),
        "updated_at": job.get("updated_at"),
    }
