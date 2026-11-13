import uuid
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app.api import decisions, memories, memory as memory_api, settings as settings_api
from app.schemas_incidents import DecisionActionCreate
from app.services import agent, memory as memory_service, seed


@pytest.mark.parametrize(
    ("source_type", "confidence", "expected_verified"),
    [
        ("user_reported_fact", 0.5, False),
        ("verified_business_fact", 0.9, True),
    ],
)
def test_memory_retain_enforces_authoritative_provenance(
    monkeypatch: pytest.MonkeyPatch,
    source_type: str,
    confidence: float,
    expected_verified: bool,
) -> None:
    organization = SimpleNamespace(id=uuid.uuid4(), memory_bank_id="test-bank")
    retained: dict = {}

    class Client:
        def retain(self, **kwargs):
            retained.update(kwargs)
            return "retained"

    class Database:
        def __init__(self) -> None:
            self.rows = []

        def add(self, row) -> None:
            self.rows.append(row)

        def commit(self) -> None:
            pass

        def refresh(self, row) -> None:
            pass

    db = Database()
    monkeypatch.setattr(memory_service, "ensure_bank", lambda *args, **kwargs: None)
    monkeypatch.setattr(memory_service, "_client", Client)
    monkeypatch.setattr(memory_service, "_close_client", lambda client: None)
    monkeypatch.setattr(
        memory_service,
        "_log",
        lambda *args, **kwargs: SimpleNamespace(id=uuid.uuid4()),
    )

    memory_service.retain(
        db,
        organization,
        content="A user reported the recovery result.",
        source_type=source_type,
        confidence=confidence,
        metadata={
            "source_type": "verified_business_fact" if not expected_verified else "user_reported_fact",
            "verified": not expected_verified,
            "confidence": 1.0,
        },
    )

    metadata = retained["metadata"]
    assert metadata["source_type"] == source_type
    assert metadata["verified"] == str(expected_verified)
    assert metadata["confidence"] == str(confidence)
    record = db.rows[0]
    assert record.source_type == source_type
    assert record.verified is expected_verified
    assert record.confidence == confidence


def test_ai_memory_context_distinguishes_reported_and_verified_evidence() -> None:
    block = agent._memory_block(
        [
            {
                "type": "experience",
                "text": "Reported outcome.",
                "provenance": {
                    "source_type": "user_reported_fact",
                    "verified": False,
                    "confidence": 0.5,
                },
            },
            {
                "type": "experience",
                "text": "Verified outcome.",
                "provenance": {
                    "source_type": "verified_business_fact",
                    "verified": True,
                    "confidence": 0.9,
                },
            },
        ],
        None,
    )

    assert "user-reported, not independently verified" in block
    assert "verified, confidence 0.9" in block


def test_decision_evidence_preserves_source_and_confidence() -> None:
    evidence = decisions._historical_evidence(
        [
            {
                "id": "reported-memory",
                "text": "Reported outcome.",
                "provenance": {
                    "source_type": "user_reported_fact",
                    "verified": False,
                    "confidence": 0.5,
                },
            }
        ],
        incident=None,
    )

    assert evidence[0]["sourceType"] == "user_reported_fact"
    assert evidence[0]["verified"] is False
    assert evidence[0]["confidence"] == 0.5


def test_memory_centre_serialization_preserves_provenance() -> None:
    record = memories._historical_memory(
        {
            "id": "memory-1",
            "content": "Reported outcome.",
            "metadata": {
                "crisis_type": "Shipment Disruption",
                "successful": True,
                "lessons_learned": "Verify the arrival time.",
            },
            "event_date": "2026-01-02T00:00:00+00:00",
            "source_type": "user_reported_fact",
            "verified": False,
            "confidence": 0.5,
        }
    )

    assert record is not None
    assert record["sourceType"] == "user_reported_fact"
    assert record["verified"] is False
    assert record["confidence"] == 0.5


def test_public_demo_user_cannot_reset_shared_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    organization = SimpleNamespace(is_demo=True, id=uuid.uuid4())
    context = SimpleNamespace(
        organization=organization,
        user=SimpleNamespace(role="procurement_manager", id=uuid.uuid4()),
    )
    reset_bank = Mock()
    monkeypatch.setattr(memory_api.memory_service, "reset_bank", reset_bank)

    with pytest.raises(HTTPException) as error:
        memory_api.reset(confirm=True, ctx=context, db=SimpleNamespace())

    assert error.value.status_code == 403
    reset_bank.assert_not_called()


def test_seed_demo_preserves_partial_existing_hindsight_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    organization = SimpleNamespace(id=uuid.uuid4())
    existing = [object()]
    db = SimpleNamespace(
        scalars=Mock(return_value=SimpleNamespace(all=lambda: existing)),
    )
    reset_bank = Mock()
    seed_memories = Mock()
    monkeypatch.setattr(seed, "_get_or_create_org", lambda db: organization)
    monkeypatch.setattr(seed, "_get_or_create_demo_user", lambda db, org: None)
    monkeypatch.setattr(seed, "seed_business_data", lambda db, org, force: {})
    monkeypatch.setattr(seed.memory_service, "reset_bank", reset_bank)
    monkeypatch.setattr(seed, "seed_memories", seed_memories)

    result = seed.seed_demo(db, force=False, retain_memories=True)

    reset_bank.assert_not_called()
    seed_memories.assert_not_called()
    assert result["memory"]["preserved_existing"] is True
    assert result["memory"]["total"] == 1


def test_memory_reset_failure_preserves_local_provenance_records(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class Client:
        def delete_bank(self, bank_id):
            raise RuntimeError("Hindsight unavailable")

    db = SimpleNamespace(scalars=Mock())
    close_client = Mock()
    monkeypatch.setattr(memory_service, "_client", Client)
    monkeypatch.setattr(memory_service, "_close_client", close_client)
    organization = SimpleNamespace(id=uuid.uuid4(), memory_bank_id="test-bank")

    with pytest.raises(memory_service.HindsightUnavailable, match="reset failed"):
        memory_service.reset_bank(db, organization)

    db.scalars.assert_not_called()
    close_client.assert_called_once()


def test_decision_action_retry_returns_existing_confirmation(monkeypatch: pytest.MonkeyPatch) -> None:
    organization_id = uuid.uuid4()
    user_id = uuid.uuid4()
    incident_id = uuid.uuid4()
    request_id = uuid.uuid4()
    incident = SimpleNamespace(
        incident_number="INC-1",
        title="Port closure",
        supplier_id=uuid.uuid4(),
        crisis_type="Shipment Disruption",
        urgency="High",
    )
    existing = SimpleNamespace(id=uuid.uuid4(), decision="accepted")
    db = SimpleNamespace(
        scalar=Mock(side_effect=[incident, existing]),
        add=Mock(),
        commit=Mock(),
    )
    context = SimpleNamespace(
        organization=SimpleNamespace(id=organization_id),
        user=SimpleNamespace(id=user_id),
    )
    payload = DecisionActionCreate(
        incidentId=str(incident_id),
        requestId=str(request_id),
        action="accepted",
        strategyKey="wait",
    )
    audit = Mock()
    monkeypatch.setattr(decisions, "audit", audit)

    response = decisions.record_decision_action(payload, context, db)

    assert response["data"]["confirmationId"] == str(existing.id)
    assert response["data"]["message"] == "Decision 'accepted' was already recorded."
    db.add.assert_not_called()
    db.commit.assert_not_called()
    audit.assert_not_called()


def test_health_endpoint_hides_dependency_exception_details(monkeypatch: pytest.MonkeyPatch) -> None:
    class Database:
        def execute(self, statement):
            raise RuntimeError("postgres://user:secret@db.internal/app")

    monkeypatch.setattr(
        settings_api.memory_service,
        "_client",
        lambda: (_ for _ in ()).throw(RuntimeError("hindsight-token=secret")),
    )
    response = settings_api.health(Database())

    assert response["status"] == "degraded"
    assert response["database"] == {"ok": False}
    assert response["hindsight"] == {"ok": False, "version": None}
    assert "secret" not in str(response)
