from utils.helpers import ZKConnection
from dotenv import load_dotenv
from datetime import datetime
import os


load_dotenv()


# Device connection configuration
IP = os.getenv("ZK_IP")
PORT = int(os.getenv("ZK_PORT"))


# User access rules configuration
BLACK_LISTED = ["user_x"]  # Users who cannot enter at all
WHITE_LISTED = ["user_z"]  # Users who can always enter (admins)
ALLOWED_HOURS = (8, 18)    # Allowed access hours (8 AM to 6 PM). Can be int 8 or str "08:36" or float 17.5 (17:30)


def get_name(user_id, all_users, all_ids):
    # we'll exploit the fact that all_ids is sorted
    l, r = 0, len(all_ids) - 1
    while l <= r:
        mid = (l + r) // 2
        if all_ids[mid] == user_id:
            return all_users[mid].name
        elif all_ids[mid] < user_id:
            l = mid + 1
        else:
            r = mid - 1
    return None


def allow_access(conn, user_id, time):
    """
    Main access control logic - determines if user should be allowed access.
    Returns True if access should be granted, False otherwise.
    """
    current_time = datetime.now().time()
    
    with conn as zk:
        
        users = zk.get_users()
        ids = [user.user_id for user in users]
        
        # check if user exists
        if user_id not in ids:
            print(f"User {user_id} does not exist in the system.")
            return False
        
        user_name = get_name(user_id, users, ids)
        
        # check if user is whitelisted
        if user_name in WHITE_LISTED:
            print(f"Access GRANTED for user {user_id} (whitelisted)")
            return True
        
        # check if user is blacklisted
        if user_name in BLACK_LISTED:
            print(f"Access DENIED for user {user_id} (blacklisted)")
            return False
    
    # normal access
    # just need to check the time
    def parse_time(hour):
        if isinstance(hour, int):
            return datetime.strptime(f"{hour}:00:00", "%H:%M:%S").time()
        elif isinstance(hour, str) and ":" in hour:
            return datetime.strptime(hour, "%H:%M").time()
        elif isinstance(hour, float):
            hours = int(hour)
            minutes = int((hour - hours) * 60)
            return datetime.strptime(f"{hours}:{minutes}:00", "%H:%M:%S").time()
        else:
            raise ValueError(f"Invalid time format: {hour}")

    start_time = parse_time(ALLOWED_HOURS[0])
    end_time = parse_time(ALLOWED_HOURS[1])

    if start_time <= current_time <= end_time:
        print(f"Access GRANTED for user {user_id} (within allowed time range)")
        return True
    else:
        print(f"Access DENIED for user {user_id} (outside allowed time range)")
        return False


def enable_device_access(conn):
    try:
        conn.unlock(time=5)  # Unlock for 5 seconds
        print("Device access enabled (door unlocked)")
        return True
    except Exception as e:
        print(f"Failed to enable device access: {e}")
        return False


def real_time_access_control(conn: ZKConnection):
    """
    Real-time access control system that monitors device events and enforces rules.
    This function continuously listens for access attempts and applies security rules.
    """
    
    with conn as zk:

        print(" LIVE CAPTURE ".center(35, "="))
        
        for attendance in zk.live_capture():
                
            if attendance is None:
                continue
            
            user_id = attendance.user_id
            
            # Apply access control rules
            if allow_access(conn, user_id):
                print(f"ACCESS GRANTED - Unlocking door for user {user_id}")
                enable_device_access(conn)
                
                # Log successful access
                
            else:
                print(f"ACCESS DENIED - Door remains locked for user {user_id}")
                
                # Log denied access
                
            print("=" * 35)