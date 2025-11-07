import asyncio
import uvicorn

from api import app
from scheduler import scheduler
from tasks import fetch_and_upload_patients, fetch_and_upload_appointments
from utils.cache import Cache
from utils.logger import get_logger

logger = get_logger(__name__)

async def setup_initial_cache():
    cache = Cache()
    await cache.connect()
    if not await cache.exists("last_patients_sync"):
        await cache.set("last_patients_sync", "never")
    if not await cache.exists("last_appointments_sync"):
        await cache.set("last_appointments_sync", "never")
    logger.info("Cache initialized ✅")


async def main():
    logger.info("🚀 Starting ReNova Collector service")

    await setup_initial_cache()

    # scheduler.add_job(
    #     fetch_and_upload_patients,
    #     seconds=60 * 15,
    #     name="patients"
    # )
    scheduler.add_job(
        fetch_and_upload_appointments,
        seconds=60 * 5,
        name="appointments"
    )
    asyncio.create_task(scheduler.run_forever())

    try:
        config = uvicorn.Config(app, host="localhost", port=8081)
        server = uvicorn.Server(config)
        await server.serve()
    except KeyboardInterrupt:
        logger.warning("🛑 Collector stopped manually")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
