from __future__ import annotations
import logging
from ..graph.workbook import WorkbookReader
from ..repositories.snapshot_repo import SnapshotRepository
from ..repositories.history_repo import HistoryRepository
from ..services.diff import DiffService
from ..notifications.base import NotifierBase
from ..models.snapshot import Snapshot

logger = logging.getLogger(__name__)


class MonitorService:
    def __init__(
        self,
        workbook_reader: WorkbookReader,
        snapshot_repo: SnapshotRepository,
        history_repo: HistoryRepository,
        notifiers: list[NotifierBase],
        key_column: str = "",
    ) -> None:
        self._reader = workbook_reader
        self._snapshot_repo = snapshot_repo
        self._history_repo = history_repo
        self._notifiers = notifiers
        self._diff = DiffService()
        self._key_column = key_column
        self._last_run: str | None = None
        self._total_records: int = 0

    async def run_cycle(self) -> None:
        logger.info("Monitor cycle started")
        try:
            rows = await self._reader.get_rows()
            key_col = self._reader.detect_key_column(rows) if not self._key_column else self._key_column
            anterior = self._snapshot_repo.load()
            atual = self._diff.build_snapshot(rows, key_col)
            events = self._diff.compare(anterior, atual, key_col)

            if events:
                self._history_repo.append(events)
                for notifier in self._notifiers:
                    for event in events:
                        try:
                            await notifier.notify(event)
                        except Exception as e:
                            logger.error(f"Notifier {notifier.__class__.__name__} error: {e}")

            self._snapshot_repo.save(atual)
            self._total_records = atual.total
            from datetime import datetime, timezone
            self._last_run = datetime.now(timezone.utc).isoformat()
            logger.info(f"Cycle done. {self._total_records} records, {len(events)} change(s)")
        except Exception as e:
            logger.exception(f"Monitor cycle error: {e}")
            raise

    @property
    def status(self) -> dict:
        return {
            "last_run": self._last_run,
            "total_records": self._total_records,
        }
