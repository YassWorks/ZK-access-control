from fastapi import FastAPI
from app.src import real_time_access_control_stream, check_security_stream
from app.utils import get_logger, ZKConnection
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import os


directory = os.path.dirname(os.path.abspath(__file__))
logs_dir = os.path.join(directory, "logs")
logger = get_logger(logs_dir)


app = FastAPI(
    title="ZKTeco Access Control and Monitoring System",
)


class SecurityMonitorRequest(BaseModel):
    ip: str
    port: int = 4370
    admin_count: int
    allowed_hours: str = "8,18"
    check_interval: int = 5


class AccessControlRequest(BaseModel):
    ip: str
    port: int = 4370
    whitelist: str  # comma-separated list of user names that match the ones on the device e.g. "x,y"
    blacklist: str  # same as above
    allowed_hours: str = "8,18"


@app.get("/")
def root():
    return {"message": "ok"}


@app.post("/security-monitor/stream")
async def security_monitor_stream(req: SecurityMonitorRequest):
    """
    Server-Sent Events endpoint for real-time security monitoring.
    Returns a continuous stream of security events.
    """

    conn = ZKConnection(ip=req.ip, port=req.port, timeout=165, ommit_ping=False)

    async def event_generator():
        try:
            async for event in check_security_stream(
                conn=conn,
                admin_count=req.admin_count,
                allowed_time_range=tuple(
                    _.strip() for _ in req.allowed_hours.split(",")
                ),
                check_interval=req.check_interval,
                logger=logger,
            ):
                print(f"=== GOT SECURITY EVENT: {event} ===")
                logger.info(f"Got event from security stream: {event}")
                yield f"data: {json.dumps(event)}\n\n"

        except Exception as e:
            print(f"=== EXCEPTION IN SECURITY GENERATOR: {e} ===")
            logger.error(f"Exception in security generator: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e), 'type': 'security_generator_exception'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )


@app.post("/access-control/stream")
async def access_control_stream(req: AccessControlRequest):
    """
    Server-Sent Events endpoint for real-time access control.
    Returns a continuous stream of access control events.
    """

    conn = ZKConnection(ip=req.ip, port=req.port, timeout=165, ommit_ping=False)

    async def event_generator():
        try:
            async for event in real_time_access_control_stream(
                conn=conn,
                whitelist=list(_.strip() for _ in req.whitelist.split(",")),
                blacklist=list(_.strip() for _ in req.blacklist.split(",")),
                allowed_hours=tuple(_.strip() for _ in req.allowed_hours.split(",")),
                logger=logger,
            ):
                print(f"=== GOT ACCESS CONTROL EVENT: {event} ===")
                logger.info(f"Got event from access control stream: {event}")
                yield f"data: {json.dumps(event)}\n\n"

        except Exception as e:
            print(f"=== EXCEPTION IN ACCESS CONTROL GENERATOR: {e} ===")
            logger.error(f"Exception in access control generator: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e), 'type': 'access_control_generator_exception'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )