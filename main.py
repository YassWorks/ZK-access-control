from fastapi import FastAPI
from src import real_time_access_control_stream, check_security_stream
from utils import get_logger, ZKConnection
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

logger = get_logger()

app = FastAPI(
    title="ZKTeco Access Control and Monitoring System",
)


class SecurityMonitorRequest(BaseModel):
    ip: str
    port: int = 4370
    admin_count: int
    allowed_hours: str = "8,18"
    check_interval: int = 30


class AccessControlRequest(BaseModel):
    ip: str
    port: int = 4370
    whitelist: str  # comma-separated list of user names that match the ones on the device e.g. "x,y"
    blacklist: str  # same as above
    allowed_hours: str = "8,18"
    check_interval: int = 30


@app.get("/")
def root():
    return {"message": "ok"}


@app.get("/security-monitor/stream")
async def security_monitor_stream(req: SecurityMonitorRequest):
    """
    Server-Sent Events endpoint for real-time security monitoring.
    Returns a continuous stream of security events.
    """

    # Setup connection and logger
    conn = ZKConnection(ip=req.ip, port=req.port, timeout=165, ommit_ping=False)
    logger = get_logger()

    async def event_generator():
        async for event in check_security_stream(
            conn=conn,
            admin_count=req,
            allowed_time_range=tuple(_.strip() for _ in req.allowed_hours.split(",")),
            check_interval=req.check_interval,
            logger=logger,
        ):
            # Format as Server-Sent Event
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )


@app.get("/access-control/stream")
async def access_control_stream(req: AccessControlRequest):
    """
    Server-Sent Events endpoint for real-time access control.
    Returns a continuous stream of access control events.
    """

    # Setup connection and logger
    conn = ZKConnection(ip=req.ip, port=req.port, timeout=165, ommit_ping=False)
    logger = get_logger()

    async def event_generator():
        async for event in real_time_access_control_stream(
            conn=conn,
            whitelist=(_.strip() for _ in req.whitelist.split(",")),
            blacklist=(_.strip() for _ in req.blacklist.split(",")),
            allowed_time_range=tuple(_.strip() for _ in req.allowed_hours.split(",")),
            check_interval=req.check_interval,
            logger=logger,
        ):
            # Format as Server-Sent Event
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )
