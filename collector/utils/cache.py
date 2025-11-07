import asyncio
import json
from typing import Any, Optional

import redis.asyncio as aioredis

from utils.config import REDIS_URL, CACHE_DEFAULT_TTL
from utils.logger import get_logger

logger = get_logger(__name__)

class Cache:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or REDIS_URL
        self._redis: Optional[aioredis.Redis] = None

    async def connect(self):
        if self._redis is None:
            self._redis = await aioredis.from_url(
                self.redis_url, encoding="utf-8", decode_responses=True
            )
            logger.info(f"Connected async to Redis at {self.redis_url}")

    async def close(self):
        if self._redis:
            await self._redis.aclose()
            logger.info("Redis async connection closed")

    async def set(self, key: str, value: Any, expire: int = CACHE_DEFAULT_TTL):
        await self.connect()
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            await self._redis.set(key, value, ex=expire)
            logger.debug(f"Cached key '{key}' for {expire}s")
        except Exception as e:
            logger.error(f"Failed to set cache for key '{key}': {e}")

    async def get(self, key: str) -> Optional[Any]:
        await self.connect()
        try:
            data = await self._redis.get(key)
            if data is None:
                logger.debug(f"Cache miss for key '{key}'")
                return None
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        except Exception as e:
            logger.error(f"Failed to get cache for key '{key}': {e}")
            return None

    async def delete(self, key: str):
        await self.connect()
        try:
            await self._redis.delete(key)
            logger.debug(f"Deleted cache key '{key}'")
        except Exception as e:
            logger.error(f"Failed to delete cache for key '{key}': {e}")

    async def clear(self):
        await self.connect()
        try:
            await self._redis.flushdb()
            logger.warning("Redis cache cleared")
        except Exception as e:
            logger.error(f"Failed to flush Redis DB: {e}")

    async def exists(self, key):
        return bool(await self._redis.exists(key))

async def main():
    # Test redis connection
    redis_cache = Cache()
    key = 'test_key'
    await redis_cache.connect()
    await redis_cache.set(key, 'test_data')
    logger.info(await redis_cache.exists(key))
    logger.info(await redis_cache.get(key))
    await redis_cache.clear()
    logger.info(await redis_cache.exists(key))
    logger.info(await redis_cache.get(key))
    await redis_cache.close()


if __name__ == '__main__':
    asyncio.run(main())