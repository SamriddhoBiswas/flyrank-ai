from redis import Redis
from rq import Queue

from app.config import QUEUE_NAME, REDIS_URL


def get_redis() -> Redis:
    return Redis.from_url(REDIS_URL)


def get_queue(connection: Redis | None = None) -> Queue:
    conn = connection or get_redis()
    return Queue(QUEUE_NAME, connection=conn)
