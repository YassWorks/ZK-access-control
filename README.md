# ZK Device Access Control & Monitoring

A simple security system for ZK biometric devices with real-time access control and monitoring.

## Quick Start

### Prerequisites
- Python 3.7+
- ZK biometric device with network connectivity

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Create `.env` file:**
```env
ZK_IP=192.168.1.100
ZK_PORT=4370
ALLOWED_HOURS=8,18
ADMIN_COUNT=2
BLACK_LISTED=user1,user2
WHITE_LISTED=admin1,admin2
```

### Usage

**Run monitoring system:**
```bash
python -m app.scripts.monitoring_script
```

**Run access control system:**
```bash
python -m app.scripts.control_script
```

**Run API server:**
```bash
uvicorn main:app --host 0.0.0.0 --port 9000
```

**Using Docker:**
```bash
docker-compose up
```

## Features

- **Real-time Access Control**: Instant approval/denial based on security rules
- **User Management**: Whitelist/blacklist functionality
- **Time-based Access**: Configurable access hours (supports various time formats)
- **Security Monitoring**: Detects off-hours access and suspicious activity
- **Admin Monitoring**: Tracks administrator privileges and counts
- **API Endpoints**: RESTful API with streaming support
- **Docker Support**: Easy containerized deployment

## Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `ZK_IP` | Device IP address | `192.168.1.100` |
| `ZK_PORT` | Device port | `4370` |
| `ALLOWED_HOURS` | Access time range | `8,18` or `08:30,17:45` |
| `ADMIN_COUNT` | Max administrators | `2` |
| `BLACK_LISTED` | Denied users | `user1,user2` |
| `WHITE_LISTED` | Always allowed users | `admin1,admin2` |

## Project Structure

```
app/
├── src/
│   ├── access_control_core.py    # Access control logic
│   └── monitor_core.py           # Security monitoring
├── scripts/
│   ├── control_script.py         # Access control service
│   └── monitoring_script.py      # Monitoring service
└── utils/
    ├── helpers.py                # ZK device utilities
    └── logger.py                 # Logging setup
```

## API Endpoints

- `GET /` - Health check
- `GET /security-monitor/stream` - Real-time security monitoring (SSE)
- `GET /access-control/stream` - Real-time access control events (SSE)

## Dependencies

- **pyzk** - ZK device communication
- **fastapi** - Web API framework
- **python-dotenv** - Environment management
- **uvicorn** - ASGI server