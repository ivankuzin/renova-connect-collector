import asyncio

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from scheduler import scheduler
from utils.logger import get_logger


logger = get_logger(__name__)

app = FastAPI(title="ReNova Collector API", version="1.0.0")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"API Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"API Response: {response.status_code} for {request.url.path}")
        return response
    except Exception as e:
        logger.exception(f"Error during request to {request.url.path}: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/status")
async def get_status():
    return {
        "time": datetime.now().isoformat(),
        "jobs": scheduler.get_status(),
    }

@app.post("/trigger")
async def trigger_job(job: str = Query(..., description="Job to trigger (patients or appointments)")):
    if job not in scheduler.jobs:
        logger.warning(f"Attempted to trigger unknown job: {job}")
        return JSONResponse(status_code=400, content={"error": "Unknown job"})
    logger.info(f"Manual trigger requested for job '{job}'")
    asyncio.create_task(scheduler.trigger_now(job))
    return {
        "status": "accepted",
        "triggered": job,
        "time": datetime.now().isoformat()
    }

@app.post("/pause")
async def pause_scheduler():
    scheduler.running = False
    logger.info("Scheduler paused manually")
    return {"status": "paused"}

@app.post("/resume")
async def resume_scheduler():
    if not scheduler.running:
        import asyncio
        asyncio.create_task(scheduler.run_forever())
        logger.info("Scheduler resumed")
        return {"status": "resumed"}
    return {"status": "already running"}
