# this file contains the loop that executes periodic checks
from utils import *
from src.monitor_core import check_security
from time import sleep
from dotenv import load_dotenv
import os

load_dotenv()
logger = get_logger()

IP = os.getenv("ZK_IP")
PORT = int(os.getenv("ZK_PORT", 4370))

conn = ZKConnection(ip=IP, port=PORT, timeout=165, ommit_ping=False)
ADMIN_COUNT = int(os.getenv("ADMIN_COUNT", 2))
ALLOWED_HOURS = tuple(os.getenv("ALLOWED_HOURS", "8,18").split(","))

first_check = True
while True:
    if first_check:
        check_security(
            conn=conn,
            admin_count=ADMIN_COUNT,
            allowed_time_range=ALLOWED_HOURS,
            first_check=first_check,
            logger=logger
        )
        first_check = False

    print("Initiating check...")
    check_security(
        conn=conn,
        admin_count=ADMIN_COUNT,
        allowed_time_range=ALLOWED_HOURS,
        first_check=first_check,
        logger=logger
    )
    sleep(10)
