"""
Source Package
Core functionality for the ZK Access Control System.
"""

from .access_control_core import (
    real_time_access_control,
    real_time_access_control_stream,
    allow_access,
    enable_device_access,
    get_name
)

from .monitor_core import (
    check_security,
    check_security_stream,
    check_attendances,
    general_check,
    check_users
)

__all__ = [
    # Access control functions
    'real_time_access_control',
    'real_time_access_control_stream',
    'allow_access',
    'enable_device_access',
    'get_name',
    
    # Monitoring functions
    'check_security',
    'check_security_stream',
    'check_attendances',
    'general_check',
    'check_users'
]