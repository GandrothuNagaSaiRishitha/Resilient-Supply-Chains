from app.api import settings as settings_api


def test_health_hides_dependency_errors_and_reports_degraded(monkeypatch):
    class BrokenDatabase:
        def execute(self, _query):
            raise RuntimeError("private database connection detail")

    class BrokenHindsight:
        def get_version(self):
            raise RuntimeError("private Hindsight endpoint detail")

        def close(self):
            pass

    monkeypatch.setattr(
        settings_api.memory_service,
        "_client",
        lambda **_kwargs: BrokenHindsight(),
    )

    response = settings_api.health(db=BrokenDatabase())

    assert response["status"] == "degraded"
    assert response["database"] == {"ok": False, "status": "unavailable"}
    assert response["hindsight"] == {
        "ok": False,
        "status": "unavailable",
        "version": None,
    }
    assert "private" not in repr(response)
