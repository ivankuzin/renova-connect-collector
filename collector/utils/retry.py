import asyncio
import functools
import random
import logging
import time

logger = logging.getLogger("retry")

def retry(
    attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    jitter: float = 0.3,
    exceptions: tuple = (Exception,),
):
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                current_delay = delay
                for attempt in range(1, attempts + 1):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        if attempt == attempts:
                            logger.error(f"{func.__name__} failed after {attempt} attempts: {e}")
                            raise
                        sleep_time = current_delay * (1 + random.uniform(-jitter, jitter))
                        logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {sleep_time:.1f}s...")
                        await asyncio.sleep(sleep_time)
                        current_delay *= backoff
            return wrapper

        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                current_delay = delay
                for attempt in range(1, attempts + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        if attempt == attempts:
                            logger.error(f"{func.__name__} failed after {attempt} attempts: {e}")
                            raise
                        sleep_time = current_delay * (1 + random.uniform(-jitter, jitter))
                        logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {sleep_time:.1f}s...")
                        time.sleep(sleep_time)
                        current_delay *= backoff
            return wrapper
    return decorator
