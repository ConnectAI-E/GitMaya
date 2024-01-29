import asyncio
import functools
import logging
import pickle
import random
from binascii import crc32
from inspect import iscoroutinefunction

import redis
from app import app

app.config.setdefault("REDIS_URL", "redis://redis:6379/0")

client = redis.from_url(app.config["REDIS_URL"], decode_responses=True)


class RedisStorage(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if v:
                self.set(k, v)

    def get(self, name):
        return client.get(name)

    def set(self, name, value):
        client.set(name, value)


def get_client(decode_responses=False):
    return redis.from_url(app.config["REDIS_URL"], decode_responses=decode_responses)


def gen_prefix(obj, method):
    return ".".join([obj.__module__, obj.__class__.__name__, method.__name__])


def stalecache(
    key=None,
    prefix=None,
    attr_key=None,
    attr_prefix=None,
    namespace="",
    expire=600,
    stale=3600,
    time_lock=1,
    time_delay=1,
    max_time_delay=10,
):
    def decorate(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            if kwargs.get("skip_cache"):
                return method(*args, **kwargs)
            name = args[0] if args and not key else None

            res = get_client(True).pipeline().ttl(name).get(name).execute()
            v = pickle.loads(res[1]) if res[0] > 0 and res[1] else None
            if res[0] <= 0 or res[0] < stale:

                def func():
                    value = method(*args, **kwargs)
                    logging.debug("update cache: %s", name)
                    get_client(True).pipeline().set(name, pickle.dumps(value)).expire(
                        name, expire + stale
                    ).execute()
                    return value

                # create new cache in blocking modal, if cache not exists.
                if res[0] <= 0:
                    return func()

                # create new cache in non blocking modal, and return stale data.
                # set expire to get a "lock", and delay to run the task
                real_time_delay = random.randrange(time_delay, max_time_delay)
                get_client(True).expire(name, stale + real_time_delay + time_lock)
                # 创建一个 asyncio 任务来执行 func
                asyncio.create_task(asyncio.sleep(real_time_delay, func()))

            return v

        @functools.wraps(method)
        async def async_wrapper(self, *args, **kwargs):
            if kwargs.get("skip_cache"):
                return await method(*args, **kwargs)

            name = args[0] if args and not key else None

            res = get_client(False).pipeline().ttl(name).get(name).execute()
            v = pickle.loads(res[1]) if res[0] > 0 and res[1] else None
            if res[0] <= 0 or res[0] < stale:

                async def func():
                    value = await method(*args, **kwargs)
                    logging.debug("update cache: %s", name)
                    get_client(False).pipeline().set(name, pickle.dumps(value)).expire(
                        name, expire + stale
                    ).execute()
                    return value

                # create new cache in blocking modal, if cache not exists.
                if res[0] <= 0:
                    return await func()

                # create new cache in non blocking modal, and return stale data.
                # set expire to get a "lock", and delay to run the task
                real_time_delay = random.randrange(time_delay, max_time_delay)
                get_client(False).expire(name, stale + real_time_delay + time_lock)
                asyncio.create_task(asyncio.sleep(real_time_delay, func()))

            return v

        return async_wrapper if iscoroutinefunction(method) else wrapper

    return decorate
