# this file contains the loop that executes periodic checks
from utils import *
from src.monitor_core import check_security
from time import sleep
from dotenv import load_dotenv
import os

load_dotenv()

IP = os.getenv("ZK_IP")
PORT = int(os.getenv("ZK_PORT", 4370))

conn = ZKConnection(ip=IP, port=PORT, timeout=165, ommit_ping=False)
ADMIN_COUNT = 2
ALLOWED_HOURS = (8, 18)


first_check = True
while True:
    if first_check:
        check_security(conn, ADMIN_COUNT, ALLOWED_HOURS, first_check)
        first_check = False
    
    print("Initiating check...")    
    check_security(conn, ADMIN_COUNT, ALLOWED_HOURS)
    sleep(10)
