from types import SimpleNamespace
from uuid import uuid4

from app.api.decisions import _historical_evidence
from app.models import MemoryRecord
from app.services import memory
from app.services.memory import provenance_for_source


def test_user_reported_memory_is_not_verified_and_confidence_is_bounded():
    assert provenance_for_source("user_reported_fact", 1.0) == (False, 0.8)


def test_verified_business_fact_preserves_valid_confidence():
    assert provenance_for_source("verified_business_fact", 0.65) == (True, 0.65)


def test_retain_persists_safe_provenance_and_protects_tenant_metadata(monkeypatch):
    class MemoryClient:
        request = None

        def retain(self, **kwargs):
            self.request = kwargs
            return "retained"

    class MemorySession:
        def __init__(self):
            self.rows = []

        def add(self, row):
            self.rows.append(row)

        def commit(self):
            pass

        def refresh(self, row):
            if isinstance(row, MemoryRecord) and row.id is None:
                row.id = uuid4()

    organization = SimpleNamespace(id=uuid4(), memory_bank_id="organization-bank")
    client = MemoryClient()
    db = MemorySession()
    monkeypatch.setattr(memory, "ensure_bank", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(memory, "_client", lambda: client)
    monkeypatch.setattr(memory, "_close_client", lambda _client: None)
    monkeypatch.setattr(
        memory,
        "_log",
        lambda *_args, **_kwargs: SimpleNamespace(id=uuid4()),
    )

    memory.retain(
        db,
        organization,
        content="User-reported outcome",
        source_type="user_reported_fact",
        confidence=1.0,
        metadata={"verified": True, "confidence": 1.0, "bank_id": "other-tenant"},
    )

    record = next(row for row in db.rows if isinstance(row, MemoryRecord))
    assert record.verified is False
    assert record.confidence == 0.8
    assert record.bank_id == "organization-bank"
    assert client.request["metadata"]["verified"] == "False"
    assert client.request["metadata"]["confidence"] == "0.8"
    assert client.request["metadata"]["bank_id"] == "organization-bank"


def test_unprovenanced_memory_is_not_described_as_verified():
    from app.services.agent import _memory_block

    result = _memory_block([{"text": "No provenance available"}], None)

    assert "unverified or unknown" in result
    assert "verified)" not in result


def test_historical_evidence_preserves_reported_provenance():
    incident = SimpleNamespace()
    evidence = _historical_evidence(
        [
            {
                "id": "reported-memory",
                "text": "User-reported outcome",
                "metadata": {"verified": "false"},
            },
            {
                "id": "verified-memory",
                "text": "Verified outcome",
                "provenance": {"verified": True},
            },
        ],
        incident,
    )

    assert [item["verified"] for item in evidence] == [False, True]


def test_non_verified_sources_are_never_marked_verified():
    assert provenance_for_source("recommendation", 2.0) == (False, 0.8)
