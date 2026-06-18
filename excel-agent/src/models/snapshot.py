from __future__ import annotations
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from .record import Record


class Snapshot(BaseModel):
    registros: list[Record]
    capturado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total: int = 0

    def model_post_init(self, __context: object) -> None:
        self.total = len(self.registros)

    def to_dict_list(self) -> list[dict]:
        return [r.dados for r in self.registros]

    def by_id(self) -> dict[str, Record]:
        return {r.id: r for r in self.registros}
