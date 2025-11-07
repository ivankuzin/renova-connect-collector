import os
from dotenv import load_dotenv

load_dotenv()

CLINICIA_EMAIL = os.getenv('CLINICIA_EMAIL')
CLINICIA_PASSWORD = os.getenv('CLINICIA_PASSWORD')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
CACHE_DEFAULT_TTL = int(os.getenv("CACHE_DEFAULT_TTL", 600))
LOG_LEVEL = os.getenv('LOG_LEVEL')
LOG_DIR = os.getenv('LOG_DIR')
