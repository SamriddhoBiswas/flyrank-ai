"""Background job: query (SQL agg) → render PDF → store artifact → update status."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from app.alerts import alert_job_failed
from app.config import JOB_MAX_RETRIES, REPORTS_DIR
from app.jobs import get_job, update_job
from app.pdf import render_sales_pdf
from app.query import fetch_report_data_sync
from app.queue import get_redis


def _jsonable(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    return value


def generate_report(job_id: str) -> dict:
    redis = get_redis()
    job = get_job(redis, job_id)
    if not job:
        raise ValueError(f"Unknown job {job_id}")

    # Idempotent: if PDF already exists, reuse it
    if job["status"] == "succeeded" and job.get("result", {}).get("download_url"):
        path = Path(job["result"].get("file_path") or "")
        if path.exists():
            print(f"[worker] report {job_id} already exists — skipping")
            return job["result"]

    attempts = int(job.get("attempts") or 0) + 1
    update_job(redis, job_id, status="running", attempts=attempts, error=None)

    try:
        raw = fetch_report_data_sync()
        data = _jsonable(raw)

        reports_dir = Path(REPORTS_DIR)
        reports_dir.mkdir(parents=True, exist_ok=True)
        filename = f"sales-report-{job_id}.pdf"
        output_path = reports_dir / filename

        title = (job.get("payload") or {}).get("title") or "Sales Report"
        render_sales_pdf(data, output_path, title=title)

        size = output_path.stat().st_size
        if size > 20 * 1024 * 1024:
            raise RuntimeError("PDF exceeds 20 MB artifact limit")

        result = {
            "filename": filename,
            "file_path": str(output_path),
            "size_bytes": size,
            "download_url": f"/reports/{job_id}/download",
            "totals": data.get("totals"),
            "categories": len(data.get("by_category") or []),
        }
        update_job(redis, job_id, status="succeeded", result=result, error=None)
        print(f"[worker] report {job_id} written → {output_path} ({size} bytes)")
        return result
    except Exception as exc:
        error = str(exc)
        update_job(redis, job_id, status="failed", error=error)
        if attempts >= JOB_MAX_RETRIES:
            alert_job_failed(job_id, error, attempts)
        raise
