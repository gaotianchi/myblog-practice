import os

import redis
from dotenv import load_dotenv

load_dotenv()

pool = redis.ConnectionPool(host=os.getenv("REDIS_HOST"))
