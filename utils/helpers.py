from zk import ZK
from typing import Optional


# Context manager to use 'with' block
class ZKConnection:
    
    def __init__(self, ip: int, port: int = 4370, timeout: int = 165, ommit_ping: bool = False):
        
        self.zk = ZK(ip, port=port, timeout=timeout, ommit_ping=ommit_ping)
        self.conn = None

    def __enter__(self):
        """Enter the runtime context related to this object."""
        
        self.conn = self.zk.connect()
        return self.conn
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context related to this object."""
        
        if self.conn:
            self.conn.disconnect()
            self.conn = None
        return False