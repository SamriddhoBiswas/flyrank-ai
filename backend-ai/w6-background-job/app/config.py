import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
ALERT_WEBHOOK_URL = os.getenv("ALERT_WEBHOOK_URL", "")
ALERT_LOG_PATH = os.getenv("ALERT_LOG_PATH", "alerts.log")
JOB_MAX_RETRIES = int(os.getenv("JOB_MAX_RETRIES", "3"))
AI_CALL_SECONDS = float(os.getenv("AI_CALL_SECONDS", "3"))
PORT = int(os.getenv("PORT", "8000"))
QUEUE_NAME = "ai_jobs"
