import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_status_no_monitor():
    from src.api.routes import status as status_route
    status_route._monitor = None
    app = FastAPI()
    app.include_router(status_route.router)
    client = TestClient(app)
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json()["status"] == "initializing"


def test_dados_no_snapshot():
    from src.api.routes import dados as dados_route
    dados_route._snapshot_repo = None
    app = FastAPI()
    app.include_router(dados_route.router)
    client = TestClient(app)
    response = client.get("/dados")
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_alteracoes_no_history():
    from src.api.routes import alteracoes as alt_route
    alt_route._history_repo = None
    app = FastAPI()
    app.include_router(alt_route.router)
    client = TestClient(app)
    response = client.get("/alteracoes")
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_registro_not_found(tmp_path):
    from src.repositories.snapshot_repo import SnapshotRepository
    from src.api.routes import registros as reg_route
    repo = SnapshotRepository(tmp_path)
    reg_route.init_router(repo)
    app = FastAPI()
    app.include_router(reg_route.router)
    client = TestClient(app)
    response = client.get("/registro/inexistente")
    assert response.status_code == 404
