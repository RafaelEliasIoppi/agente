from __future__ import annotations
from pathlib import Path
from ..models.snapshot import Snapshot
from ..storage.file_storage import read_json, write_json


class SnapshotRepository:
    def __init__(self, snapshots_dir: Path) -> None:
        self._path = snapshots_dir / "snapshot_atual.json"

    def load(self) -> Snapshot | None:
        data = read_json(self._path)
        if data is None:
            return None
        return Snapshot.model_validate(data)

    def save(self, snapshot: Snapshot) -> None:
        write_json(self._path, snapshot.model_dump(mode="json"))
