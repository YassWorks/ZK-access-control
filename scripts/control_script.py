# this file contains the loop that manages access to door in real-time
from utils import *
from dotenv import load_dotenv
import os
from src.access_control_core import real_time_access_control


logger = get_logger()
load_dotenv()


# Device connection configuration
IP = os.getenv("ZK_IP")
PORT = int(os.getenv("ZK_PORT"))


# User access rules configuration
BLACK_LISTED = ["user_x"]  # Users who cannot enter at all (by name not id)
WHITE_LISTED = ["user_z"]  # Users who can always enter (admins) (by name not id)
ALLOWED_HOURS = (8, 18)    # Allowed access hours (8 AM to 6 PM). Can be int 8 or str "08:36" or float 17.5 (17:30)


conn = ZKConnection(ip=IP, port=PORT, timeout=165, ommit_ping=False)


try:
    real_time_access_control(
        conn=conn,
        blacklist=BLACK_LISTED,
        whitelist=WHITE_LISTED,
        allowed_hours=ALLOWED_HOURS,
        logger=logger
    )
except KeyboardInterrupt:
    print("Exiting control script...")
except Exception as e:
    logger.error(f"An error occurred: {e}")
    print(f"An error occurred: {e}")