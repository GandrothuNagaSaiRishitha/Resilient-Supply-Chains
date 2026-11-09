from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock
import uuid

import pytest

from app.api import decision_replays
from app.services.memory import HindsightUnavailable


def replay_context():
    organization = SimpleNamespace(id=uuid.uuid4())
    incident = SimpleNamespace(
        id=uuid.uuid4(),
        organization_id=organization.id,
        crisis_type="Shipment Disruption",
        title="Port delay",
        product_component="MCU-1000",
        incident_date=datetime(2026, 11, 9, tzinfo=timezone.utc),
        created_at=None,
        affected_orders=2,
    )
    context = SimpleNamespace(
        organization=organization,
        user=SimpleNamespace(id=uuid.uuid4()),
    )
    scenario = {
        "strategies": [{"key": "wait"}],
        "recommendedStrategyKey": "wait",
    }
    return incident, context, scenario


@pytest.mark.parametrize(
    ("recall_result", "expected_status", "expected_key", "explanation"),
    [
        (HindsightUnavailable("offline"), "unavailable", None, "Hindsight is unavailable"),
        ({"results": []}, "empty", None, "no relevant memories"),
        (
            {"results": [{"id": "memory-1", "text": "Observed outcome", "provenance": {"strategy_key": "wait"}}]},
            "available",
            "wait",
            "1 Hindsight memories were retrieved",
        ),
    ],
)
def test_replay_record_reports_actual_hindsight_status(
    monkeypatch, recall_result, expected_status, expected_key, explanation
):
    incident, context, scenario = replay_context()
    db = SimpleNamespace(
        scalar=Mock(return_value=incident),
        scalars=Mock(return_value=SimpleNamespace(all=lambda: [])),
    )
    monkeypatch.setattr(decision_replays, "build_scenario", Mock(return_value=scenario))
    if isinstance(recall_result, Exception):
        monkeypatch.setattr(decision_replays.memory_service, "recall", Mock(side_effect=recall_result))
    else:
        monkeypatch.setattr(decision_replays.memory_service, "recall", Mock(return_value=recall_result))

    response = decision_replays.replay_record(incident.id, context, db)["data"]

    assert response["memoryStatus"] == expected_status
    assert response["memoryInformedStrategyKey"] == expected_key
    assert explanation in response["evidenceExplanation"]
    if expected_status != "available":
        assert response["historicalEvidence"] == []


def test_run_replay_does_not_claim_hindsight_recall_when_unavailable(monkeypatch):
    incident, context, scenario = replay_context()
    db = SimpleNamespace(scalar=Mock(return_value=incident), commit=Mock())
    monkeypatch.setattr(decision_replays, "build_scenario", Mock(return_value=scenario))
    monkeypatch.setattr(
        decision_replays.memory_service,
        "recall",
        Mock(side_effect=HindsightUnavailable("offline")),
    )
    monkeypatch.setattr(decision_replays, "audit", Mock())

    response = decision_replays.run_replay(incident.id, context, db)["data"]

    assert response["memoryStatus"] == "unavailable"
    assert "Hindsight is unavailable" in response["message"]
    assert "0 Hindsight memories" not in response["message"]
