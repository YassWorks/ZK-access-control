from zk import ZK
from zk.base import Attendance
from zk.base import User
from typing import Optional


# Context manager to use 'with' block
class ZKConnection:
    
    def __init__(self, ip: str, port: int = 4370, timeout: int = 165, ommit_ping: bool = False):
        
        self.zk = ZK(ip, port=port, timeout=timeout, ommit_ping=ommit_ping)
        self.conn = None

    def __enter__(self):
        """Enter the runtime context related to this object."""
        
        try:
            self.conn = self.zk.connect()
            return self.conn
        except Exception as e:
            raise ConnectionError(f"Failed to connect to the device: {e}")
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context related to this object."""
        
        if self.conn:
            try:
                self.conn.disconnect()
            except Exception as e:
                print(f"Error while disconnecting: {e}")
        else:
            print("No connection to disconnect.")
        
        self.conn = None


def get_attendances(conn: ZKConnection) -> Optional[list[Attendance]]:
    
    with conn as zk:
        
        attendances = zk.get_attendance()
        return attendances


def get_users(conn: ZKConnection) -> Optional[list[User]]:
    
    with conn as zk:
        
        users = zk.get_users()
        return users