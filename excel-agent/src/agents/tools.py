from __future__ import annotations
import json
import logging
from datetime import date, datetime
from typing import Any
from langchain_core.tools import tool
from ..repositories.snapshot_repo import SnapshotRepository
from ..repositories.history_repo import HistoryRepository

logger = logging.getLogger(__name__)

_snapshot_repo: SnapshotRepository | None = None
_history_repo: HistoryRepository | None = None


def init_tools(snapshot_repo: SnapshotRepository, history_repo: HistoryRepository) -> None:
    global _snapshot_repo, _history_repo
    _snapshot_repo = snapshot_repo
    _history_repo = history_repo


def _get_registros() -> list[dict[str, Any]]:
    if _snapshot_repo is None:
        raise RuntimeError("Tools not initialized")
    snap = _snapshot_repo.load()
    if snap is None:
        return []
    return [r.dados for r in snap.registros]


@tool
def contar_registros() -> str:
    """Conta o total de registros atualmente na planilha."""
    registros = _get_registros()
    return f"Total de registros: {len(registros)}"


@tool
def buscar_todos_registros() -> str:
    """Retorna todos os registros da planilha como JSON."""
    registros = _get_registros()
    return json.dumps(registros[:50], ensure_ascii=False, default=str)


@tool
def filtrar_por_campo(campo: str, valor: str) -> str:
    """Filtra registros onde o campo especificado contém o valor (case-insensitive)."""
    registros = _get_registros()
    resultado = [
        r for r in registros
        if valor.lower() in str(r.get(campo, "")).lower()
    ]
    return json.dumps(resultado, ensure_ascii=False, default=str)


@tool
def filtrar_por_status(status: str) -> str:
    """Filtra registros por status/situação."""
    registros = _get_registros()
    status_cols = ["status", "Status", "STATUS", "situacao", "Situação", "state"]
    resultado = []
    for r in registros:
        for col in status_cols:
            if col in r and status.lower() in str(r[col]).lower():
                resultado.append(r)
                break
    return json.dumps(resultado, ensure_ascii=False, default=str)


@tool
def buscar_alteracoes_hoje() -> str:
    """Retorna todos os eventos de alteração ocorridos hoje."""
    if _history_repo is None:
        raise RuntimeError("Tools not initialized")
    events = _history_repo.load_today()
    return json.dumps([e.model_dump(mode="json") for e in events], ensure_ascii=False, default=str)


@tool
def buscar_todas_alteracoes() -> str:
    """Retorna todo o histórico de alterações."""
    if _history_repo is None:
        raise RuntimeError("Tools not initialized")
    events = _history_repo.load_all()
    return json.dumps([e.model_dump(mode="json") for e in events[-100:]], ensure_ascii=False, default=str)


@tool
def buscar_por_id(id_registro: str) -> str:
    """Busca um registro específico pelo seu ID."""
    if _snapshot_repo is None:
        raise RuntimeError("Tools not initialized")
    snap = _snapshot_repo.load()
    if snap is None:
        return "Nenhum snapshot disponível"
    record = snap.by_id().get(id_registro)
    if record is None:
        return f"Registro com ID '{id_registro}' não encontrado"
    return json.dumps(record.dados, ensure_ascii=False, default=str)


TOOLS = [
    contar_registros,
    buscar_todos_registros,
    filtrar_por_campo,
    filtrar_por_status,
    buscar_alteracoes_hoje,
    buscar_todas_alteracoes,
    buscar_por_id,
]
