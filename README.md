# Remote Access Control & Monitoring System for ZK Devices

A comprehensive security solution for ZK biometric devices providing real-time access control, security monitoring, and automated alerts.

## Quick Start

### Prerequisites
- Python 3.7+
- ZK device with TCP/IP connectivity
- Network access to the device

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure `.env` file:
```env
ZK_IP=192.168.1.100
ZK_PORT=4370
ALLOWED_HOURS=8,18
ADMIN_COUNT=2
BLACK_LISTED=user1,user2
WHITE_LISTED=admin1,admin2
```

### Usage

**Start monitoring system:**
```bash
python -m scripts.monitoring_script
# or
./launch_monitor.sh
```

**Start access control system:**
```bash
python -m scripts.control_script
# or
./launch_secure_access.sh
```

## Features

### Access Control
- **Real-time Decision Making**: Instant access approval/denial based on security rules
- **Whitelist/Blacklist Management**: Permanent allow/deny lists for users
- **Time-based Access**: Configurable access hours with flexible time formats
- **Automatic Door Control**: Unlocks device for authorized users

### Security Monitoring
- **Off-hours Access Detection**: Alerts for access attempts outside allowed times
- **Rapid Entry Detection**: Identifies potential security breaches from consecutive entries
- **Admin Privilege Monitoring**: Tracks administrator account count and privileges
- **Device Time Sync**: Ensures accurate timekeeping for security logs
- **Password Security**: Identifies accounts without passwords

### Logging & Alerts
- Comprehensive logging to files and console
- Real-time security violation alerts
- Configurable notification system

## Project Structure

```
├── src/
│   ├── access_control_core.py    # Real-time access control logic
│   └── monitor_core.py           # Security monitoring functions
├── scripts/
│   ├── control_script.py         # Access control daemon
│   └── monitoring_script.py      # Security monitoring daemon
├── utils/
│   ├── helpers.py                # ZK device utilities
│   └── logger.py                 # Logging configuration
└── logs/                         # Generated log files
```

## Configuration

### Environment Variables
- `ZK_IP`: Device IP address
- `ZK_PORT`: Device port (default: 4370)
- `ALLOWED_HOURS`: Access time range (format: "start,end" - supports int, float, or "HH:MM")
- `ADMIN_COUNT`: Maximum allowed administrators
- `BLACK_LISTED`: Comma-separated list of denied users
- `WHITE_LISTED`: Comma-separated list of always-allowed users

## Dependencies
- `pyzk`: ZK device communication library
- `python-dotenv`: Environment variable management