from __future__ import annotations
from datetime import datetime, timezone, date
from pathlib import Path
from ..models.record import ChangeEvent
from ..storage.file_storage import read_json, write_json, append_json_list


class HistoryRepository:
    def __init__(self, history_dir: Path) -> None:
        self._path = history_dir / "historico_alteracoes.json"

    def append(self, events: list[ChangeEvent]) -> None:
        if not events:
            return
        append_json_list(self._path, [e.model_dump(mode="json") for e in events])

    def load_all(self) -> list[ChangeEvent]:
        data = read_json(self._path) or []
        return [ChangeEvent.model_validate(item) for item in data]

    def load_today(self) -> list[ChangeEvent]:
        today = date.today()
        return [
            e for e in self.load_all()
            if e.timestamp.date() == today
        ]
