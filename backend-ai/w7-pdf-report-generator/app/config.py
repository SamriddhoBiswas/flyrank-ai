import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://reportuser:reportpass@localhost:5432/reportdb"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REPORTS_DIR = os.getenv("REPORTS_DIR", "data/reports")
ALERT_LOG_PATH = os.getenv("ALERT_LOG_PATH", "alerts.log")
JOB_MAX_RETRIES = int(os.getenv("JOB_MAX_RETRIES", "3"))
PORT = int(os.getenv("PORT", "8000"))
QUEUE_NAME = "report_jobs"
