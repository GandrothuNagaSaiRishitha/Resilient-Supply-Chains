from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api import memory as memory_api
from app.services import memory


def demo_context():
    return SimpleNamespace(
        user=SimpleNamespace(id=uuid4(), role="owner"),
        organization=SimpleNamespace(
            id=uuid4(),
            memory_bank_id="demo-bank",
            is_demo=True,
        ),
    )


def test_demo_memory_reset_requires_a_server_token(monkeypatch):
    monkeypatch.setattr(
        memory_api,
        "get_settings",
        lambda: SimpleNamespace(demo_memory_reset_token=None),
    )

    with pytest.raises(HTTPException) as error:
        memory_api.reset(confirm=True, reset_token=None, ctx=demo_context(), db=object())

    assert error.value.status_code == 503


def test_demo_memory_reset_validates_token_before_reset(monkeypatch):
    ctx = demo_context()
    calls = []
    monkeypatch.setattr(
        memory_api,
        "get_settings",
        lambda: SimpleNamespace(demo_memory_reset_token="server-only-token"),
    )
    monkeypatch.setattr(memory_api.memory_service, "reset_bank", lambda *_args: calls.append("reset"))
    monkeypatch.setattr(memory_api, "audit", lambda *_args: calls.append("audit"))

    with pytest.raises(HTTPException) as error:
        memory_api.reset(confirm=True, reset_token="wrong-token", ctx=ctx, db=object())

    assert error.value.status_code == 403
    assert calls == []


def test_hindsight_delete_failure_does_not_remove_local_provenance(monkeypatch):
    class FailingClient:
        def delete_bank(self, _bank_id):
            raise RuntimeError("Hindsight unavailable")

    class MemorySession:
        queried = False

        def scalars(self, _query):
            self.queried = True
            raise AssertionError("Local provenance must not be deleted on remote failure")

    db = MemorySession()
    monkeypatch.setattr(memory, "_client", FailingClient)
    monkeypatch.setattr(memory, "_close_client", lambda _client: None)
    monkeypatch.setattr(
        memory,
        "ensure_bank",
        lambda *_args, **_kwargs: pytest.fail("A failed remote delete must not recreate the bank"),
    )

    with pytest.raises(memory.HindsightUnavailable):
        memory.reset_bank(db, demo_context().organization)

    assert db.queried is False
