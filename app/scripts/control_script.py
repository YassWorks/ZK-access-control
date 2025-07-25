# this file contains the loop that manages access to door in real-time
from app.utils import get_logger, ZKConnection
from dotenv import load_dotenv
import os
from app.src.access_control_core import real_time_access_control

logger = get_logger()
load_dotenv()

# device connection configuration
IP = os.getenv("ZK_IP")
PORT = int(os.getenv("ZK_PORT"))

# user access rules configuration
BLACK_LISTED = list(os.getenv("BLACK_LISTED", "").split(","))
WHITE_LISTED = list(os.getenv("WHITE_LISTED", "").split(","))
ALLOWED_HOURS = tuple(os.getenv("ALLOWED_HOURS", "8,18").split(","))

conn = ZKConnection(ip=IP, port=PORT, timeout=165, ommit_ping=False)

try:
    real_time_access_control(
        conn=conn,
        blacklist=BLACK_LISTED,
        whitelist=WHITE_LISTED,
        allowed_hours=ALLOWED_HOURS,
        logger=logger,
    )
except Exception as e:
    logger.error(f"An error occurred: {e}")
    print(f"An error occurred: {e}")
finally:
    print("Control script terminated.")
