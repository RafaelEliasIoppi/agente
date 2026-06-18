from __future__ import annotations
from typing import Any, Literal
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_serializer


class Record(BaseModel):
    id: str
    dados: dict[str, Any]
    snapshot_ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def get_field(self, campo: str) -> Any:
        return self.dados.get(campo)


class ChangeEvent(BaseModel):
    tipo: Literal["NOVA_LINHA", "EXCLUSAO", "ALTERACAO", "MUDANCA_STATUS"]
    linha_id: str
    campo: str | None = None
    valor_antigo: Any = None
    valor_novo: Any = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_serializer("timestamp")
    def serialize_timestamp(self, v: datetime) -> str:
        return v.isoformat()
