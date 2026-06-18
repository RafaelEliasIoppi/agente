import pytest
from src.services.diff import DiffService
from src.models.snapshot import Snapshot


@pytest.fixture
def diff():
    return DiffService()


def make_rows(data):
    return data


def test_no_changes(diff):
    rows = [{"id": "1", "nome": "Rafael", "status": "Ativo"}]
    snap1 = diff.build_snapshot(rows, key_col="id")
    snap2 = diff.build_snapshot(rows, key_col="id")
    events = diff.compare(snap1, snap2, "id")
    assert events == []


def test_nova_linha(diff):
    rows1 = [{"id": "1", "nome": "Rafael"}]
    rows2 = [{"id": "1", "nome": "Rafael"}, {"id": "2", "nome": "Maria"}]
    snap1 = diff.build_snapshot(rows1, "id")
    snap2 = diff.build_snapshot(rows2, "id")
    events = diff.compare(snap1, snap2, "id")
    assert len(events) == 1
    assert events[0].tipo == "NOVA_LINHA"
    assert events[0].linha_id == "2"


def test_exclusao(diff):
    rows1 = [{"id": "1"}, {"id": "2"}]
    rows2 = [{"id": "1"}]
    snap1 = diff.build_snapshot(rows1, "id")
    snap2 = diff.build_snapshot(rows2, "id")
    events = diff.compare(snap1, snap2, "id")
    assert len(events) == 1
    assert events[0].tipo == "EXCLUSAO"
    assert events[0].linha_id == "2"


def test_alteracao_campo(diff):
    rows1 = [{"id": "1", "nome": "Rafael"}]
    rows2 = [{"id": "1", "nome": "Rafael Ioppi"}]
    snap1 = diff.build_snapshot(rows1, "id")
    snap2 = diff.build_snapshot(rows2, "id")
    events = diff.compare(snap1, snap2, "id")
    assert len(events) == 1
    assert events[0].tipo == "ALTERACAO"
    assert events[0].campo == "nome"
    assert events[0].valor_antigo == "Rafael"
    assert events[0].valor_novo == "Rafael Ioppi"


def test_mudanca_status(diff):
    rows1 = [{"id": "1", "status": "Pendente"}]
    rows2 = [{"id": "1", "status": "Concluído"}]
    snap1 = diff.build_snapshot(rows1, "id")
    snap2 = diff.build_snapshot(rows2, "id")
    events = diff.compare(snap1, snap2, "id")
    assert len(events) == 1
    assert events[0].tipo == "MUDANCA_STATUS"


def test_first_run_no_events(diff):
    rows = [{"id": "1", "nome": "Rafael"}]
    snap = diff.build_snapshot(rows, "id")
    events = diff.compare(None, snap, "id")
    assert events == []
