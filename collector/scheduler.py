import asyncio
from datetime import datetime, timedelta
from utils.logger import get_logger
# from uploader import upload_patients, upload_appointments

logger = get_logger(__name__)

class Scheduler:
    def __init__(self):
        self.jobs = {}
        self.running = False

    def add_job(self, func, seconds: int, name=None):
        name = name or func.__name__
        self.jobs[name] = {
            "interval": timedelta(seconds=seconds),
            "last_run": None,
            "func": func
        }
        logger.info(f"Scheduled job '{name}' every {seconds}s")

    async def run_forever(self):
        self.running = True
        logger.info("Scheduler started")
        while self.running:
            now = datetime.now()
            for name, job in self.jobs.items():
                last_run = job["last_run"]
                if not last_run or now - last_run >= job["interval"]:
                    logger.info(f"Running scheduled job: {name}")
                    await self._run_job(name)
            await asyncio.sleep(60)

    async def _run_job(self, name: str):
        job = self.jobs.get(name)
        if not job:
            logger.warning(f"Tried to run unknown job: {name}")
            return
        try:
            await job["func"]()
            job["last_run"] = datetime.now()
            logger.info(f"Job '{name}' completed successfully")
        except Exception as e:
            logger.exception(f"Job '{name}' failed: {e}")

    async def trigger_now(self, name: str):
        logger.info(f"Manual trigger for job: {name}")
        await self._run_job(name)

    def get_status(self):
        return {
            name: {
                "last_run": job["last_run"].isoformat() if job["last_run"] else None,
                "interval_minutes": job["interval"].seconds // 60,
                "next_run_in": (
                    (job["interval"] - (datetime.now() - job["last_run"])).seconds // 60
                    if job["last_run"] else 0
                )
            }
            for name, job in self.jobs.items()
        }

scheduler = Scheduler()
