import hashlib
import json

import aiohttp

from utils.cache import Cache
from utils.logger import get_logger
from utils.retry import retry

logger = get_logger(__name__)

class Uploader:

    def __init__(self, base_url: str = "http://transform-api:8000", api_key: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.cache = Cache()

    @staticmethod
    def _hash_data(data: list | dict) -> str:
        normalized = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha1(normalized.encode()).hexdigest()

    async def _should_upload(self, endpoint: str, new_data: list | dict) -> bool:
        key = f"{endpoint}_hash"
        old_hash = await self.cache.get(key)
        new_hash = self._hash_data(new_data)

        if not old_hash:
            logger.info(f"No previous hash found for {endpoint}, will upload.")
            return True

        if new_hash != old_hash:
            logger.info(f"Detected changes in {endpoint}, will upload.")
            return True

        logger.info(f"No changes in {endpoint}, skipping upload.")
        return False

    @retry(attempts=1, delay=5)
    async def _post(self, endpoint: str, data: list | dict):
        logger.info(f'{endpoint} - {len(data)}')
        return # TODO: remove once Transform API is ready
        # url = f"{self.base_url}/{endpoint}"
        # headers = {"Content-Type": "application/json"}
        # if self.api_key:
        #     headers["Authorization"] = f"Bearer {self.api_key}"
        #
        # async with aiohttp.ClientSession() as session:
        #     async with session.post(url, headers=headers, json=data) as response:
        #         if response.status != 200:
        #             text = await response.text()
        #             raise Exception(f"Upload failed [{response.status}]: {text}")
        #         logger.info(f"✅ Uploaded {endpoint} ({len(data)} records)")
        #         return await response.json()

    async def upload_patients(self, patients: list[dict]):
        if not await self._should_upload("patients", patients):
            return "skipped"

        await self._post("patients", patients)
        new_hash = self._hash_data(patients)
        await self.cache.set("patients_hash", new_hash)
        logger.info("📦 Patients uploaded and hash updated.")
        return "uploaded"

    async def upload_appointments(self, appointments: list[dict]):
        if not await self._should_upload("appointments", appointments):
            return "skipped"

        await self._post("appointments", appointments)
        new_hash = self._hash_data(appointments)
        await self.cache.set("appointments_hash", new_hash)
        logger.info("📦 Appointments uploaded and hash updated.")
        return "uploaded"
