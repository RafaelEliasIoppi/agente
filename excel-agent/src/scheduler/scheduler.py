from __future__ import annotations
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class MonitorScheduler:
    def __init__(self, interval_seconds: int = 300) -> None:
        self._scheduler = AsyncIOScheduler()
        self._interval = interval_seconds

    def add_job(self, func, *args, **kwargs) -> None:
        self._scheduler.add_job(
            func,
            trigger=IntervalTrigger(seconds=self._interval),
            args=args,
            kwargs=kwargs,
            id="monitor_job",
            replace_existing=True,
            misfire_grace_time=60,
        )
        logger.info(f"Scheduled monitor job every {self._interval}s")

    def start(self) -> None:
        self._scheduler.start()
        logger.info("Scheduler started")

    def shutdown(self) -> None:
        self._scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
