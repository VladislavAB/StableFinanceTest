import os
from contextlib import asynccontextmanager
import redis.asyncio as redis
from fastapi import HTTPException

REDIS_URL = os.getenv("REDIS_URL")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


@asynccontextmanager
async def redis_lock(lock_key: str, expire: int = 5):
    acquired = await redis_client.set(lock_key, "_", nx=True, ex=expire)

    if not acquired:
        raise HTTPException(status_code=404, detail="Этот мерчант уже обрабатыватся")

    try:
        yield
    finally:
        await redis_client.delete(lock_key)
