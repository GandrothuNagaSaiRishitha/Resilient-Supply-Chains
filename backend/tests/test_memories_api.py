from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api import memories as memories_api
from app.deps import get_current_context
from app.db import get_db
from app.main import app


@pytest.mark.parametrize(
    "path",
    ["/api/memories/overview", "/api/memories", "/api/memories/memory-id"],
)
def test_memory_centre_routes_return_503_when_hindsight_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
    path: str,
) -> None:
    organization = SimpleNamespace(memory_bank_id="test-bank")
    context = SimpleNamespace(organization=organization)
    record = {"id": "memory-id", "content": "Incident outcome"}
    previous_overrides = app.dependency_overrides.copy()

    def fail_recall(*args, **kwargs):
        raise memories_api.memory_service.HindsightUnavailable("connection refused")

    monkeypatch.setattr(memories_api.memory_service, "records", lambda *args, **kwargs: [record])
    monkeypatch.setattr(memories_api.memory_service, "recall", fail_recall)
    app.dependency_overrides[get_current_context] = lambda: context
    app.dependency_overrides[get_db] = lambda: None

    try:
        response = TestClient(app).get(path)
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Hindsight memory retrieval is unavailable. Check the Hindsight service and try again."
    }
