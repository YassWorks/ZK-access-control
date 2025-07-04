# Remote Access Control & Monitoring System for ZK Devices

A comprehensive security monitoring solution for ZK biometric devices, providing real-time surveillance, anomaly detection, and automated security alerts for facial recognition access control systems.

## Quick Start

### Prerequisites
- Python 3.7+
- Network access to ZK device
- ZK device with TCP/IP connectivity enabled

### Installation

1. Clone the repository

3. Configure the `.env` file with `ZK_IP` and `ZK_PORT` ofd your device

4. Run the monitoring system:
```bash
python -m script
```

## 🔧 Configuration

### Security Parameters
- **Admin Count**: Maximum allowed administrator users
- **Time Range**: Allowed access hours (24-hour format). Example: (8, 18) (8am -> 6pm)

## Project Structure

```
internship-remote-access-control/
├── core.py              # Core security monitoring functions
├── script.py            # Main execution script with monitoring loop
├── utils/
│   ├── __init__.py     # Package initialization
│   └── helpers.py      # ZK device connection utilities
├── requirements.txt     # Python dependencies
└── README.md           # Project documentation
```

## Security Checks

### 1. Attendance Monitoring
- **Off-hours Access**: Detects access attempts outside allowed time range
- **Rapid Consecutive Entries**: Identifies potential security breaches
- **Access Pattern Analysis**: Monitors unusual access behaviors

### 2. System Security
- **Device Time Sync**: Ensures device time accuracy
- **Admin Privilege Control**: Monitors administrator account count
- **Password Security**: Identifies accounts without passwords

### 3. Real-time Alerts
- Security violations trigger immediate alerts
- Configurable notification system (WhatsApp integration ready)

## Docs

### Core Functions

#### `check_security(conn, admin_count, allowed_time_range, first_check=False)`
Main security monitoring function that performs comprehensive checks.

#### `check_attendances(conn, allowed_time_range, first_check=False)`
Monitors attendance records for security violations.

#### `check_users(conn, admin_count, first_check)`
Audits user accounts and privileges.

#### `general_check(conn)`
Performs general system health and security checks.

#### `ZKConnection`
Context manager for secure ZK device connections. Because I like working with the `with` block.

## TODO

- logging (file and stout)
- more security checks

---

feedback welcome <3