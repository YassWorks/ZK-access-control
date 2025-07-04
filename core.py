from utils import *
from collections import defaultdict
from datetime import datetime
from zk.base import const


def check_security(conn: ZKConnection, admin_count: int, allowed_time_range: tuple = (8, 18), first_check: bool = False):
    
    general_check(conn)
    check_users(conn, admin_count, first_check)
    check_attendances(conn, allowed_time_range, first_check)


def check_attendances(conn: ZKConnection, allowed_time_range: tuple = (8, 18), first_check: bool = False):
    
    with conn as zk:
        # check if attendances times are within the allowed range
        attendances = zk.get_attendance()
        if not attendances:
            print("No attendances found.")
        
        check_range = None # attendances concerned with this iteration
        
        if first_check:
            check_range = attendances
        else:
            # Only check the first 3 attendances if there are more than 3
            # This is to avoid overwhelming the system with too many checks
            # and to focus on the most recent entries.
            # I think 3 is a good numner to balance overlap between iterations and ensure security.
            if len(attendances) < 3:
                check_range = attendances
            else:
                check_range = attendances[:3]
        
        for attendance in check_range:
            attendance_time = attendance.timestamp.hour
            if attendance_time < allowed_time_range[0] or attendance_time > allowed_time_range[1]:
                print(f"Security alert! Attendance at {attendance.timestamp} is outside the allowed range.")
                # send whatsapp msg
        
        user_times = defaultdict(list)
        
        for att in check_range:
            user_times[att.user_id].append(att.timestamp)
        
        # Check for spam (per user)
        for user_id, times in user_times.items():
            times.sort()
            for i in range(1, len(times)):
                time_diff = (times[i] - times[i-1]).total_seconds()
                if time_diff < 30:  # < 30 sec
                    print(f"Security Alert: Rapid consecutive entries for user {user_id}")
                    # send whatsapp msg


def general_check(conn: ZKConnection):
    
    with conn as zk:
        device_time = zk.get_time()
        system_time = datetime.now()
        time_diff = abs((device_time - system_time).total_seconds())
        
        if time_diff > 300: # 5 minutes tolerance
            print(f"Security Alert: Device time drift detected ({time_diff} seconds)")
            # send whatsapp msg


def check_users(conn: ZKConnection, admin_count: int, first_check: bool):
    
    with conn as zk:
        users = zk.get_users()
        if not users:
            print("No users found.")
            return

        admin_users = [u for u in users if u.privilege == const.USER_ADMIN]
        if len(admin_users) > admin_count:
            print(f"Security Alert: Too many admin users ({len(admin_users)})")
            # send whatsapp msg
        
        if first_check:
            # check if users with no password exist
            # this is annoying to loop so we keep it for the first check
            for user in users:
                if not user.password or user.password == '':
                    print(f"Security Alert: User {user.user_id} has no password set.")
                    # send whatsapp msg