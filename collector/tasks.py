from datetime import datetime

from clinicia_client import CliniciaClient
from utils.config import CLINICIA_EMAIL, CLINICIA_PASSWORD
from uploader import Uploader
from utils.cache import Cache
from utils.logger import get_logger

logger = get_logger(__name__)

async def fetch_and_upload_patients():
    logger.info("🚀 Starting task: fetch_and_upload_patients")

    async with CliniciaClient(
        email="demo@clinic.com",
        password="password"
    ) as client:
        patients = await client.get_patients()

    if not patients:
        logger.warning("No patients found.")
        return

    uploader = Uploader()
    await uploader.upload_patients(patients)

    cache = Cache()
    await cache.set("last_patients_sync", datetime.now().isoformat())
    logger.info(f"✅ Uploaded {len(patients)} patients and updated cache timestamp.")


async def fetch_and_upload_appointments():
    logger.info("🚀 Starting task: fetch_and_upload_appointments")

    async with CliniciaClient(
        email=CLINICIA_EMAIL,
        password=CLINICIA_PASSWORD
    ) as client:
        appointments = await client.get_appointments()

    if not appointments:
        logger.warning("No appointments found.")
        return

    uploader = Uploader()
    await uploader.upload_appointments(appointments)

    cache = Cache()
    await cache.set("last_appointments_sync", datetime.now().isoformat())
    logger.info(f"✅ Uploaded {len(appointments)} appointments and updated cache timestamp.")
