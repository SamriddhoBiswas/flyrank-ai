from redis import Redis
from rq import Worker

from app.config import QUEUE_NAME, REDIS_URL


def main() -> None:
    connection = Redis.from_url(REDIS_URL)
    print(f"Report worker listening on '{QUEUE_NAME}' ({REDIS_URL})")
    Worker([QUEUE_NAME], connection=connection).work(with_scheduler=True)


if __name__ == "__main__":
    main()
