from utils.helpers import ZKConnection, parse_time
from datetime import datetime
import traceback
from zk import ZK
import time

def get_name(user_id, all_users: list, all_ids: list):
    """
    Helper function to get the name of a user by their ID.
    Returns the name if found, otherwise returns the ID itself.
    """
    try:
        index = all_ids.index(user_id)
        return all_users[index].name
    except ValueError:
        return None


def allow_access(zk: ZK, user_id, whitelist: list[str] = None, blacklist: list[str] = None, allowed_hours: tuple = None):
    """
    Main access control logic - determines if user should be allowed access.
    Returns True if access should be granted, False otherwise.
    """
    
    current_time = datetime.now().time()
    
    users = zk.get_users()
    ids = [user.user_id for user in users]
    
    # check if user exists
    if user_id not in ids:
        print(f"User {user_id} does not exist in the system.")
        return False
    
    user_name = get_name(user_id, users, ids)
    print(f"Checking access for user {user_name} (ID: {user_id}) at {current_time}")
    
    # check if user is whitelisted
    if whitelist and user_name in whitelist:
        print(f"Access GRANTED for user {user_id} (whitelisted)")
        return True
    
    # check if user is blacklisted
    if blacklist and user_name in blacklist:
        print(f"Access DENIED for user {user_id} (blacklisted)")
        return False
    
    # if no time restrictions are set, allow access
    if not allowed_hours:
        print(f"Access GRANTED for user {user_id} (no time restrictions)")
        return True
    
    # validate allowed_hours format
    if len(allowed_hours) != 2:
        print(f"Invalid allowed_hours format. Expected tuple of 2 elements, got {len(allowed_hours)}.")
        return False
    
    # normal access - check the time
    try:
        start_time = parse_time(allowed_hours[0])
        end_time = parse_time(allowed_hours[1])
    except ValueError as e:
        print(f"Error parsing time format: {e}")
        return False

    if start_time <= current_time <= end_time:
        print(f"Access GRANTED for user {user_id} (within allowed time range)")
        return True
    else:
        print(f"Access DENIED for user {user_id} (outside allowed time range)")
        return False


def enable_device_access(zk: ZK):
    try:
        zk.unlock(time=5)  # Unlock for 5 seconds
        print("Device access enabled (door unlocked)")
        return True
    except Exception as e:
        print(f"Failed to enable device access: {e}")
        return False


def real_time_access_control(conn: ZKConnection, logger=None, whitelist=None, blacklist=None, allowed_hours=None):
    """
    Real-time access control system that monitors device events and enforces rules.
    This function continuously listens for access attempts and applies security rules.
    """
    
    print(" LIVE CAPTURE ".center(35, "="))
    if logger:
        logger.info("Starting live capture for access control")
    
    while True:
        try:
            with conn as zk:
                for attendance in zk.live_capture():
                    # zk.disable_device()
                
                    if attendance is None:
                        continue
                    
                    user_id = attendance.user_id
                    
                    # Apply access control rules
                    if allow_access(zk, user_id, whitelist=whitelist, blacklist=blacklist, allowed_hours=allowed_hours):
                        print(f"ACCESS GRANTED - Unlocking door for user {user_id}")
                        # zk.enable_device()
                        enable_device_access(zk)
                        
                        if logger:
                            logger.info(f"Access granted for user {user_id} at {datetime.now()}")
                        
                    else:
                        print(f"ACCESS DENIED - Door remains locked for user with id {user_id}")
                        
                        # # Immediately disable device to prevent further access
                        # zk.disable_device()
                        
                        # # Play deny sound/voice
                        zk.test_voice(2)  # Access Denied voice
                        
                        # # Re-enable after a short delay
                        # time.sleep(2)
                        # zk.enable_device()
                        
                        if logger:
                            logger.info(f"Access denied for user {user_id} at {datetime.now()}")
                        
                    print("=" * 35)
                    
        except KeyboardInterrupt:
            print("\nAccess control monitoring stopped by user.")
            if logger:
                logger.info("Access control monitoring stopped by user interrupt")
            break
        except Exception as e:
            error_msg = f"Error in access control monitoring: {e}"
            print(error_msg)
            traceback.print_exc()
            if logger:
                logger.error(error_msg)
            print("Continuing monitoring...\n")
