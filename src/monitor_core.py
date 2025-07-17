from utils import *
from utils.helpers import parse_time
from collections import defaultdict
from datetime import datetime
from zk.base import const
import asyncio
from typing import AsyncGenerator, Dict, Any
import time
import traceback


def check_security(
    conn: ZKConnection,
    admin_count: int,
    allowed_time_range: tuple = (8, 18),
    check_interval: int = 10,
    logger=None,
):
    """
    Main security check function that continuously performs the following checks:
    1. General device time check
    2. User checks (admin count, password checks)
    3. Attendance checks (time range, spam detection)

    This function runs in an infinite loop until interrupted by Ctrl+C.
    """

    print(" SECURITY MONITORING ".center(35, "="))
    if logger:
        logger.info("Starting security monitoring")

    first_check = True

    while True:
        try:
            if first_check:
                print("Performing initial comprehensive security check...")
                if logger:
                    logger.info("Performing initial comprehensive security check")
            else:
                print("Initiating security check...")
                if logger:
                    logger.info("Initiating periodic security check")

            general_check(conn, logger=logger)
            check_users(conn, admin_count, first_check, logger=logger)
            check_attendances(conn, allowed_time_range, first_check, logger=logger)

            if first_check:
                print("Initial security check completed.")
                if logger:
                    logger.info("Initial security check completed")
                first_check = False
            else:
                print("Security check completed.")
                if logger:
                    logger.info("Security check completed")

            print("=" * 35)

            time.sleep(check_interval)

        except KeyboardInterrupt:
            print("\nSecurity monitoring stopped by user.")
            if logger:
                logger.info("Security monitoring stopped by user interrupt")
            break
        except Exception as e:
            error_msg = f"Error in security monitoring: {e}"
            print(error_msg)
            traceback.print_exc()
            if logger:
                logger.error(error_msg)
            print("Continuing monitoring...\n")
            time.sleep(5)  # brief delay before retrying


def check_attendances(
    conn: ZKConnection,
    allowed_time_range: tuple = (8, 18),
    first_check: bool = False,
    logger=None,
):

    if not allowed_time_range or len(allowed_time_range) != 2:
        print("Invalid allowed_time_range provided. Skipping attendance time checks.")
        if logger:
            logger.warning(
                "Invalid allowed_time_range provided. Skipping attendance time checks."
            )
        return

    with conn as zk:
        # check if attendances times are within the allowed range
        attendances = zk.get_attendance()
        if not attendances:
            print("No attendances found.")
            if logger:
                logger.warning("No attendances found.")

        check_range = None  # attendances concerned with this iteration

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

            attendance_time = attendance.timestamp.time()

            try:
                start_time = parse_time(allowed_time_range[0])
                end_time = parse_time(allowed_time_range[1])
            except ValueError as e:
                print(f"Error parsing time format in attendance check: {e}")
                if logger:
                    logger.error(f"Error parsing time format in attendance check: {e}")
                continue

            if not (start_time <= attendance_time <= end_time):
                print(
                    f"Security alert! Attendance at {attendance.timestamp} is outside the allowed range ({start_time} - {end_time})."
                )
                if logger:
                    logger.warning(
                        f"Security alert! Attendance at {attendance.timestamp} is outside the allowed range ({start_time} - {end_time})."
                    )

        user_times = defaultdict(list)

        for att in check_range:
            user_times[att.user_id].append(att.timestamp)

        # Check for spam (per user)
        for user_id, times in user_times.items():
            times.sort()
            for i in range(1, len(times)):
                time_diff = (times[i] - times[i - 1]).total_seconds()
                if time_diff < 30:  # < 30 sec
                    print(
                        f"Security Alert: Rapid consecutive entries for user {user_id}"
                    )
                    if logger:
                        logger.warning(
                            f"Security Alert: Rapid consecutive entries for user {user_id}"
                        )


def general_check(conn: ZKConnection, logger=None):

    with conn as zk:
        device_time = zk.get_time()
        system_time = datetime.now()
        time_diff = abs((device_time - system_time).total_seconds())

        if time_diff > 300:  # 5 minutes tolerance
            print(f"Security Alert: Device time drift detected ({time_diff} seconds)")
            if logger:
                logger.warning(
                    f"Security Alert: Device time drift detected ({time_diff} seconds)"
                )


def check_users(conn: ZKConnection, admin_count: int, first_check: bool, logger=None):

    with conn as zk:
        users = zk.get_users()
        if not users:
            print("No users found.")
            return

        admin_users = [u for u in users if u.privilege == const.USER_ADMIN]
        if len(admin_users) > admin_count:
            print(f"Security Alert: Too many admin users ({len(admin_users)})")
            if logger:
                logger.warning(
                    f"Security Alert: Too many admin users ({len(admin_users)})"
                )

        if first_check:
            # check if users with no password exist
            # this is annoying to loop so we keep it for the first check
            for user in users:
                if not user.password or user.password == "":
                    print(f"Security Alert: User {user.user_id} has no password set.")
                    if logger:
                        logger.warning(
                            f"Security Alert: User {user.user_id} has no password set."
                        )


async def check_security_stream(
    conn: ZKConnection,
    admin_count: int,
    allowed_time_range: tuple = (8, 18),
    check_interval: int = 30,
    logger=None,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Async generator version of check_security for streaming endpoints.
    Continuously performs security checks and yields results as they occur.

    Args:
        conn: ZKConnection instance
        admin_count: Expected number of admin users
        allowed_time_range: Tuple of allowed hours (start, end)
        check_interval: Seconds between security checks
        logger: Logger instance
    """

    print(" SECURITY MONITORING STREAM ".center(35, "="))
    if logger:
        logger.info("Starting security monitoring stream")

    first_check = True

    while True:
        try:
            timestamp = datetime.now().isoformat()

            # General device checks
            async for event in general_check_stream(conn, logger):
                yield event

            # User checks
            async for event in check_users_stream(
                conn, admin_count, first_check, logger
            ):
                yield event

            # Attendance checks
            async for event in check_attendances_stream(
                conn, allowed_time_range, first_check, logger
            ):
                yield event

            # Yield periodic status update
            yield {
                "event_type": "security_check_complete",
                "timestamp": timestamp,
                "message": "Security check cycle completed",
                "check_interval": check_interval,
            }

            first_check = False

            # Wait before next check cycle
            await asyncio.sleep(check_interval)

        except KeyboardInterrupt:
            print("\nSecurity monitoring stream stopped by user.")
            if logger:
                logger.info("Security monitoring stream stopped by user interrupt")
            yield {
                "event_type": "system_shutdown",
                "timestamp": datetime.now().isoformat(),
                "message": "Security monitoring stopped by user",
            }
            break
        except Exception as e:
            error_msg = f"Error in security monitoring stream: {e}"
            print(error_msg)
            if logger:
                logger.error(error_msg)

            yield {
                "event_type": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "message": error_msg,
            }

            await asyncio.sleep(1)  # brief delay before retrying


async def general_check_stream(
    conn: ZKConnection, logger=None
) -> AsyncGenerator[Dict[str, Any], None]:
    """Stream version of general_check"""

    with conn as zk:
        device_time = zk.get_time()
        system_time = datetime.now()
        time_diff = abs((device_time - system_time).total_seconds())

        if time_diff > 300:  # 5 minutes tolerance
            message = (
                f"Security Alert: Device time drift detected ({time_diff} seconds)"
            )
            print(message)
            if logger:
                logger.warning(message)

            yield {
                "event_type": "time_drift_alert",
                "timestamp": datetime.now().isoformat(),
                "device_time": device_time.isoformat(),
                "system_time": system_time.isoformat(),
                "time_diff_seconds": time_diff,
                "message": message,
                "severity": "warning",
            }


async def check_users_stream(
    conn: ZKConnection, admin_count: int, first_check: bool, logger=None
) -> AsyncGenerator[Dict[str, Any], None]:
    """Stream version of check_users"""

    with conn as zk:
        users = zk.get_users()
        if not users:
            yield {
                "event_type": "no_users_found",
                "timestamp": datetime.now().isoformat(),
                "message": "No users found on device",
                "severity": "warning",
            }
            return

        admin_users = [u for u in users if u.privilege == const.USER_ADMIN]
        if len(admin_users) > admin_count:
            message = f"Security Alert: Too many admin users ({len(admin_users)})"
            print(message)
            if logger:
                logger.warning(message)

            yield {
                "event_type": "excess_admin_users",
                "timestamp": datetime.now().isoformat(),
                "admin_count": len(admin_users),
                "expected_count": admin_count,
                "admin_users": [
                    {"user_id": u.user_id, "name": u.name} for u in admin_users
                ],
                "message": message,
                "severity": "warning",
            }

        if first_check:
            # Check for users with no password
            for user in users:
                if not user.password or user.password == "":
                    message = (
                        f"Security Alert: User {user.user_id} has no password set."
                    )
                    print(message)
                    if logger:
                        logger.warning(message)

                    yield {
                        "event_type": "user_no_password",
                        "timestamp": datetime.now().isoformat(),
                        "user_id": user.user_id,
                        "user_name": user.name,
                        "message": message,
                        "severity": "warning",
                    }


async def check_attendances_stream(
    conn: ZKConnection,
    allowed_time_range: tuple = (8, 18),
    first_check: bool = False,
    logger=None,
) -> AsyncGenerator[Dict[str, Any], None]:
    """Stream version of check_attendances"""

    if not allowed_time_range or len(allowed_time_range) != 2:
        yield {
            "event_type": "invalid_time_range",
            "timestamp": datetime.now().isoformat(),
            "message": "Invalid allowed_time_range provided. Skipping attendance time checks.",
            "severity": "warning",
        }
        return

    with conn as zk:
        attendances = zk.get_attendance()
        if not attendances:
            yield {
                "event_type": "no_attendances",
                "timestamp": datetime.now().isoformat(),
                "message": "No attendances found",
                "severity": "info",
            }
            return

        check_range = (
            attendances
            if first_check
            else (attendances[:3] if len(attendances) >= 3 else attendances)
        )

        # Check time range violations
        for attendance in check_range:
            attendance_time = attendance.timestamp.time()

            try:
                start_time = parse_time(allowed_time_range[0])
                end_time = parse_time(allowed_time_range[1])
            except ValueError as e:
                yield {
                    "event_type": "time_parse_error",
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e),
                    "message": f"Error parsing time format in attendance check: {e}",
                    "severity": "error",
                }
                continue

            if not (start_time <= attendance_time <= end_time):
                message = f"Security alert! Attendance at {attendance.timestamp} is outside the allowed range ({start_time} - {end_time})."
                print(message)
                if logger:
                    logger.warning(message)

                yield {
                    "event_type": "attendance_time_violation",
                    "timestamp": datetime.now().isoformat(),
                    "attendance_time": attendance.timestamp.isoformat(),
                    "user_id": attendance.user_id,
                    "allowed_start": start_time.isoformat(),
                    "allowed_end": end_time.isoformat(),
                    "message": message,
                    "severity": "warning",
                }

        # Check for spam (rapid consecutive entries)
        user_times = defaultdict(list)
        for att in check_range:
            user_times[att.user_id].append(att.timestamp)

        for user_id, times in user_times.items():
            times.sort()
            for i in range(1, len(times)):
                time_diff = (times[i] - times[i - 1]).total_seconds()
                if time_diff < 30:  # < 30 sec
                    message = (
                        f"Security Alert: Rapid consecutive entries for user {user_id}"
                    )
                    print(message)
                    if logger:
                        logger.warning(message)

                    yield {
                        "event_type": "rapid_entry_spam",
                        "timestamp": datetime.now().isoformat(),
                        "user_id": user_id,
                        "time_diff_seconds": time_diff,
                        "entry_times": [t.isoformat() for t in times[i - 1 : i + 1]],
                        "message": message,
                        "severity": "warning",
                    }
