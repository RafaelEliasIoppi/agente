from fastapi import APIRouter, HTTPException
from ...repositories.snapshot_repo import SnapshotRepository

router = APIRouter()
_snapshot_repo: SnapshotRepository | None = None


def init_router(snapshot_repo: SnapshotRepository) -> None:
    global _snapshot_repo
    _snapshot_repo = snapshot_repo


@router.get("/registro/{id}")
async def get_registro(id: str):
    if _snapshot_repo is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    snap = _snapshot_repo.load()
    if snap is None:
        raise HTTPException(status_code=404, detail="No snapshot available")
    record = snap.by_id().get(id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Record '{id}' not found")
    return record.dados
