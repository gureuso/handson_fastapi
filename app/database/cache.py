import uuid
from redis import asyncio as aioredis

from config import Config

cache = aioredis.from_url(f'redis://{Config.REDIS_HOST}')


class Cache:
    @staticmethod
    async def add_ticket(key: str):
        ticket = str(uuid.uuid4())
        await cache.rpush(key, ticket)
        return ticket

    @staticmethod
    async def is_ticket_first(key: str, ticket: str):
        arr = await cache.lrange(key, 0, -1)
        if not arr:
            return False
        if arr[0].decode() != ticket:
            return False
        return True

    @staticmethod
    async def keys(pattern: str = '*'):
        return await cache.keys(pattern)

    @staticmethod
    async def get(key: str):
        data = await cache.get(key)
        return data.decode() if data else None

    @staticmethod
    async def set(key: str, value: str):
        return await cache.set(key, value)

    @staticmethod
    async def setex(key: str, second: int, value: str):
        return await cache.setex(key, second, value)

    @staticmethod
    async def delete(key: str):
        return await cache.delete(key)

    @staticmethod
    async def rpush(key: str, value: str):
        return await cache.rpush(key, value)

    @staticmethod
    async def lrange(key: str, start: int, end: int):
        return await cache.lrange(key, start, end)
