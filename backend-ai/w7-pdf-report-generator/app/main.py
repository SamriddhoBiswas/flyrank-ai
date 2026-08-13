"""
PDF report generator API.

POST /reports              → 202 Accepted (enqueue PDF generation)
GET  /reports/{id}         → status + download link (not the file bytes)
GET  /reports/{id}/download → stream stored PDF artifact
POST /reports/schedule     → stretch: enqueue a delayed/scheduled report
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI, Header
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from rq import Retry

from app.config import JOB_MAX_RETRIES, REPORTS_DIR
from app.jobs import create_job, get_job, get_job_id_for_idempotency
from app.queue import get_queue, get_redis
from app.tasks import generate_report

app = FastAPI(
    title="PDF Report Generator",
    description="Query → aggregate → render PDF as a background job. Store artifact, return a link.",
    version="1.0",
)


class ReportCreate(BaseModel):
    title: str = Field("Sales Report", min_length=1, max_length=120)


class ScheduleCreate(BaseModel):
    title: str = Field("Scheduled Sales Report", min_length=1, max_length=120)
    delay_seconds: int = Field(30, ge=5, le=3600, description="Run this many seconds from now")


@app.get("/")
def root():
    return {
        "name": "PDF Report Generator",
        "version": "1.0",
        "pattern": "accept fast → worker renders PDF → poll status → download link",
        "endpoints": [
            "POST /reports",
            "GET /reports/{job_id}",
            "GET /reports/{job_id}/download",
            "POST /reports/schedule",
            "GET /health",
        ],
    }


@app.get("/health")
def health():
    get_redis().ping()
    return {"status": "ok"}


@app.post("/reports", status_code=202)
def enqueue_report(
    body: ReportCreate,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    """On-demand report: returns 202 immediately; worker builds the PDF."""
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
                        "status_url": f"/reports/{existing_id}",
                        "idempotent_replay": True,
                    },
                )

    job_id = str(uuid.uuid4())
    create_job(redis, job_id, {"title": body.title}, idempotency_key=idempotency_key)

    get_queue(redis).enqueue(
        generate_report,
        job_id,
        job_id=job_id,
        retry=Retry(max=JOB_MAX_RETRIES, interval=[2, 4, 8]),
        failure_ttl=86400,
        result_ttl=86400,
    )

    return {
        "job_id": job_id,
        "status": "queued",
        "status_url": f"/reports/{job_id}",
        "message": "Report job accepted. Poll status_url, then use download_url.",
    }


@app.post("/reports/schedule", status_code=202)
def schedule_report(body: ScheduleCreate):
    """Stretch: schedule a report to run after delay_seconds."""
    redis = get_redis()
    job_id = str(uuid.uuid4())
    run_at = datetime.now(timezone.utc) + timedelta(seconds=body.delay_seconds)

    create_job(
        redis,
        job_id,
        {"title": body.title, "scheduled_for": run_at.isoformat()},
    )

    get_queue(redis).enqueue_at(
        run_at,
        generate_report,
        job_id,
        job_id=job_id,
        retry=Retry(max=JOB_MAX_RETRIES, interval=[2, 4, 8]),
    )

    return {
        "job_id": job_id,
        "status": "queued",
        "scheduled_for": run_at.isoformat(),
        "status_url": f"/reports/{job_id}",
        "message": f"Report scheduled to run in {body.delay_seconds}s.",
    }


@app.get("/reports/{job_id}")
def report_status(job_id: str):
    job = get_job(get_redis(), job_id)
    if not job:
        return JSONResponse(status_code=404, content={"error": f"Report {job_id} not found"})

    result = job.get("result") or {}
    return {
        "job_id": job["id"],
        "status": job["status"],
        "attempts": job.get("attempts", 0),
        "download_url": result.get("download_url"),
        "filename": result.get("filename"),
        "size_bytes": result.get("size_bytes"),
        "totals": result.get("totals"),
        "error": job.get("error"),
        "created_at": job.get("created_at"),
        "updated_at": job.get("updated_at"),
    }


@app.get("/reports/{job_id}/download")
def download_report(job_id: str):
    """Serve the stored PDF artifact by link — never embed the file in JSON."""
    job = get_job(get_redis(), job_id)
    if not job:
        return JSONResponse(status_code=404, content={"error": f"Report {job_id} not found"})
    if job["status"] != "succeeded":
        return JSONResponse(
            status_code=409,
            content={"error": f"Report not ready (status={job['status']})"},
        )

    result = job.get("result") or {}
    path = Path(result.get("file_path") or (Path(REPORTS_DIR) / f"sales-report-{job_id}.pdf"))
    if not path.exists():
        return JSONResponse(status_code=404, content={"error": "PDF file missing on disk"})

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=result.get("filename") or path.name,
    )
