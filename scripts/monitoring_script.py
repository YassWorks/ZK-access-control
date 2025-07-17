# this file contains the loop that executes periodic checks
from utils import *
from src.monitor_core import check_security
from dotenv import load_dotenv
import os

logger = get_logger()
load_dotenv()

# device connection configuration
IP = os.getenv("ZK_IP")
PORT = int(os.getenv("ZK_PORT", 4370))

# user access rules configuration
ADMIN_COUNT = int(os.getenv("ADMIN_COUNT", 2))
ALLOWED_HOURS = tuple(os.getenv("ALLOWED_HOURS", "8,18").split(","))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 10))

conn = ZKConnection(ip=IP, port=PORT, timeout=165, ommit_ping=False)

try:
    check_security(
        conn=conn,
        admin_count=ADMIN_COUNT,
        allowed_time_range=ALLOWED_HOURS,
        check_interval=CHECK_INTERVAL,
        logger=logger,
    )
except Exception as e:
    logger.error(f"An error occurred: {e}")
    print(f"An error occurred: {e}")
finally:
    print("Monitoring script terminated.")
