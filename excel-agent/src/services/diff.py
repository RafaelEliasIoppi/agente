from __future__ import annotations
import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any
import pandas as pd
from ..models.record import Record, ChangeEvent
from ..models.snapshot import Snapshot

logger = logging.getLogger(__name__)

STATUS_COLUMNS = {"status", "Status", "STATUS", "situacao", "Situação", "state"}


def _make_id(row_data: dict[str, Any], key_col: str, index: int) -> str:
    if key_col == "__row_index__":
        return str(index)
    value = row_data.get(key_col, "")
    return str(value) if value else hashlib.md5(json.dumps(row_data, sort_keys=True).encode()).hexdigest()[:8]


class DiffService:
    def build_snapshot(
        self, rows: list[dict[str, Any]], key_col: str
    ) -> Snapshot:
        records = [
            Record(id=_make_id(row, key_col, i), dados=row)
            for i, row in enumerate(rows)
        ]
        return Snapshot(registros=records)

    def compare(
        self, anterior: Snapshot | None, atual: Snapshot, key_col: str
    ) -> list[ChangeEvent]:
        if anterior is None:
            logger.info("No previous snapshot — skipping diff")
            return []

        events: list[ChangeEvent] = []
        ts = datetime.now(timezone.utc)

        old_map = anterior.by_id()
        new_map = atual.by_id()

        for row_id, new_rec in new_map.items():
            if row_id not in old_map:
                events.append(ChangeEvent(
                    tipo="NOVA_LINHA",
                    linha_id=row_id,
                    valor_novo=new_rec.dados,
                    timestamp=ts,
                ))
            else:
                old_rec = old_map[row_id]
                for col in new_rec.dados:
                    old_val = old_rec.dados.get(col)
                    new_val = new_rec.dados.get(col)
                    if old_val != new_val:
                        tipo = "MUDANCA_STATUS" if col in STATUS_COLUMNS else "ALTERACAO"
                        events.append(ChangeEvent(
                            tipo=tipo,
                            linha_id=row_id,
                            campo=col,
                            valor_antigo=old_val,
                            valor_novo=new_val,
                            timestamp=ts,
                        ))

        for row_id in old_map:
            if row_id not in new_map:
                events.append(ChangeEvent(
                    tipo="EXCLUSAO",
                    linha_id=row_id,
                    valor_antigo=old_map[row_id].dados,
                    timestamp=ts,
                ))

        logger.info(f"Diff complete: {len(events)} change(s) detected")
        return events
