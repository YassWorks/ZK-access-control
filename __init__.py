"""
ZK Access Control System
A comprehensive access control system for ZK devices with real-time monitoring and security checks.
"""

from .src.access_control_core import real_time_access_control, allow_access, enable_device_access
from .src.monitor_core import check_security, check_attendances, general_check, check_users
from .utils import ZKConnection, get_attendances, get_users, get_logger

__version__ = "1.0.0"
__author__ = "YassWorks"

__all__ = [
    # Core access control functions
    'real_time_access_control',
    'allow_access',
    'enable_device_access',
    
    # Monitoring functions
    'check_security',
    'check_attendances',
    'general_check',
    'check_users',
    
    # Utilities
    'ZKConnection',
    'get_attendances',
    'get_users',
    'get_logger'
]