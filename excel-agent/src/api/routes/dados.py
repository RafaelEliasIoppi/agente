from fastapi import APIRouter
from ...repositories.snapshot_repo import SnapshotRepository

router = APIRouter()
_snapshot_repo: SnapshotRepository | None = None


def init_router(snapshot_repo: SnapshotRepository) -> None:
    global _snapshot_repo
    _snapshot_repo = snapshot_repo


@router.get("/dados")
async def get_dados():
    if _snapshot_repo is None:
        return {"registros": [], "total": 0}
    snap = _snapshot_repo.load()
    if snap is None:
        return {"registros": [], "total": 0}
    return {"registros": snap.to_dict_list(), "total": snap.total, "capturado_em": snap.capturado_em}
