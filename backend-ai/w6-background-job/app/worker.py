"""RQ worker process — pull jobs from Redis and run them."""

from __future__ import annotations

from redis import Redis
from rq import Worker

from app.config import QUEUE_NAME, REDIS_URL


def main() -> None:
    connection = Redis.from_url(REDIS_URL)
    print(f"Worker listening on queue '{QUEUE_NAME}' ({REDIS_URL})")
    worker = Worker([QUEUE_NAME], connection=connection)
    worker.work(with_scheduler=True)


if __name__ == "__main__":
    main()
