import redis
from app import app

app.config.setdefault("REDIS_URL", "redis://redis:6379/0")

client = redis.from_url(app.config["CELERY_BROKER_URL"], decode_responses=True)


class RedisStorage(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if v:
                self.set(k, v)

    def get(self, name):
        return client.get(name)

    def set(self, name, value):
        client.set(name, value)
