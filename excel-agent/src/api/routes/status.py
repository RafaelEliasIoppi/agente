from fastapi import APIRouter
from ...services.monitor import MonitorService

router = APIRouter()
_monitor: MonitorService | None = None


def init_router(monitor: MonitorService) -> None:
    global _monitor
    _monitor = monitor


@router.get("/status")
async def get_status():
    if _monitor is None:
        return {"status": "initializing"}
    return {"status": "ok", **_monitor.status}
