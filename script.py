# this file will contain the loop that executes periodic checks
from utils import *


conn = ZKConnection(ip="192.128.1.26", port=4370, timeout=165, ommit_ping=False)


