from fastapi import APIRouter
from ...repositories.history_repo import HistoryRepository

router = APIRouter()
_history_repo: HistoryRepository | None = None


def init_router(history_repo: HistoryRepository) -> None:
    global _history_repo
    _history_repo = history_repo


@router.get("/alteracoes")
async def get_alteracoes():
    if _history_repo is None:
        return {"alteracoes": [], "total": 0}
    events = _history_repo.load_all()
    return {"alteracoes": [e.model_dump(mode="json") for e in events], "total": len(events)}


@router.get("/alteracoes/hoje")
async def get_alteracoes_hoje():
    if _history_repo is None:
        return {"alteracoes": [], "total": 0}
    events = _history_repo.load_today()
    return {"alteracoes": [e.model_dump(mode="json") for e in events], "total": len(events)}
