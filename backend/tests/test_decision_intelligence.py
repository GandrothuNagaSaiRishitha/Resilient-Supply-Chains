from datetime import date
import json
from types import SimpleNamespace
import uuid
from unittest.mock import Mock

import pytest

from app.api import decisions
from app.services.agent import AgentService, AgentUnavailable, DecisionRecommendationOutput
from app.services.memory import HindsightUnavailable


STRATEGIES = [
    {
        "key": "wait",
        "name": "Wait and Monitor",
        "feasibility": "Feasible",
        "additionalCost": 0,
        "deliveryDelayDays": 4,
        "projectedShortageUnits": 10,
        "feasibilityNote": "Monitor the shipment.",
        "tradeOff": "Lowest cost, longest exposure.",
    },
    {
        "key": "reroute",
        "name": "Reroute Shipments",
        "feasibility": "Feasible",
        "additionalCost": 120,
        "deliveryDelayDays": 1,
        "projectedShortageUnits": 10,
        "feasibilityNote": "Route capacity must be confirmed.",
        "tradeOff": "Higher freight cost for a shorter delay.",
    },
]
SCENARIO = {
    "summary": "Shipment disruption for control boards.",
    "strategies": STRATEGIES,
    "recommendedStrategyKey": "wait",
    "recommendationExplanation": "Wait is the lowest-cost feasible baseline.",
}


def _route_context():
    organization = SimpleNamespace(id=uuid.uuid4(), name="Northstar", memory_bank_id="org_bank")
    user = SimpleNamespace(id=uuid.uuid4(), email="buyer@example.test", role="owner")
    incident = SimpleNamespace(
        id=uuid.uuid4(),
        organization_id=organization.id,
        incident_number="INC-0001",
        crisis_type="Shipment Disruption",
        title="Port closure",
        description="A port closure delayed control board shipments.",
        supplier_id=uuid.uuid4(),
        order_id=uuid.uuid4(),
        product_component="control board",
        origin="Port A",
        destination="Warehouse B",
        expected_delay_days=4,
        available_inventory_quantity=20,
        affected_orders=3,
        urgency="High",
        incident_date=date(2026, 11, 8),
    )
    supplier = SimpleNamespace(name="Northstar Components")
    db = SimpleNamespace(scalar=Mock(side_effect=[incident, supplier]))
    context = SimpleNamespace(organization=organization, user=user)
    return db, context, incident


def _generated_recommendation(evidence_ids=None):
    return {
        "strategy_key": "reroute",
        "rationale": "Rerouting limits the reported delay while retaining the baseline cost and feasibility checks.",
        "estimated_impact": "The scenario estimates one day of delay and 120 additional cost units.",
        "risks": ["Confirm route capacity before execution."],
        "trade_offs": ["Higher freight cost for a shorter delay."],
        "evidence_ids": evidence_ids or [],
    }


def test_structured_groq_recommendation_uses_incident_memory_and_reflection(monkeypatch):
    service = AgentService(db=None, organization=SimpleNamespace(name="Northstar"), user=None)
    memory = {
        "id": "memory-1",
        "lessonLearned": "A previous reroute reduced delay but increased freight cost.",
    }
    captured = {}

    def fake_call(messages, tools, model, max_tokens=1400, response_format=None, max_attempts=None):
        captured["messages"] = messages
        captured["tools"] = tools
        captured["response_format"] = response_format
        captured["max_attempts"] = max_attempts
        payload = {
            "strategy_key": "reroute",
            "rationale": "A prior reroute reduced delay, and the current scenario supports the same option.",
            "estimated_impact": "One day of delay with additional freight cost.",
            "risks": ["Confirm route capacity."],
            "trade_offs": ["Higher freight cost."],
            "evidence_ids": ["memory-1"],
        }
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))])

    monkeypatch.setattr(service, "_call_model", fake_call)
    result = service.generate_decision_recommendation(
        incident={"crisisType": "Shipment Disruption", "supplier": "Northstar Components"},
        scenario=SCENARIO,
        historical_evidence=[memory],
        reflection="Prior reroute reduced delay at higher cost.",
    )

    assert result["strategy_key"] == "reroute"
    assert result["evidence_ids"] == ["memory-1"]
    assert captured["tools"] == []
    assert captured["response_format"] == {"type": "json_object"}
    assert captured["max_attempts"] == 1
    prompt = captured["messages"][1]["content"]
    prompt_payload = json.loads(prompt)
    assert "Northstar Components" in prompt
    assert "A previous reroute reduced delay" in prompt
    assert "Prior reroute reduced delay" in prompt
    assert prompt_payload["retrieved_memories"][0]["verified"] is False


def test_structured_groq_recommendation_rejects_unretrieved_evidence(monkeypatch):
    service = AgentService(db=None, organization=SimpleNamespace(name="Northstar"), user=None)
    payload = {
        **_generated_recommendation(["not-retrieved"]),
        "strategy_key": "reroute",
    }
    response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))])
    monkeypatch.setattr(service, "_call_model", lambda *args, **kwargs: response)

    with pytest.raises(AgentUnavailable, match="not retrieved"):
        service.generate_decision_recommendation(
            incident={"crisisType": "Shipment Disruption"},
            scenario=SCENARIO,
            historical_evidence=[{"id": "memory-1", "lessonLearned": "Actual memory."}],
            reflection=None,
        )


def test_structured_groq_recommendation_rejects_unknown_strategy(monkeypatch):
    service = AgentService(db=None, organization=SimpleNamespace(name="Northstar"), user=None)
    payload = {**_generated_recommendation(), "strategy_key": "invented-strategy"}
    response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))])
    monkeypatch.setattr(service, "_call_model", lambda *args, **kwargs: response)

    with pytest.raises(AgentUnavailable, match="outside the supplied recovery scenario"):
        service.generate_decision_recommendation(
            incident={"crisisType": "Shipment Disruption"},
            scenario=SCENARIO,
            historical_evidence=[],
            reflection=None,
        )


def test_decision_report_recalls_and_reflects_once_in_authenticated_org(monkeypatch):
    db, context, incident = _route_context()
    recalled_hit = {
        "id": "hit-1",
        "document_id": "memory-1",
        "text": "A previous port reroute reduced delay by three days.",
        "metadata": {"crisis_type": "Shipment Disruption", "successful": True, "verified": True},
        "provenance": {
            "crisis_type": "Shipment Disruption",
            "successful": True,
            "verified": True,
            "source_type": "verified_business_fact",
            "confidence": 0.9,
            "strategy_key": "reroute",
            "event_date": "2026-10-01",
            "lessons_learned": "A previous port reroute reduced delay by three days.",
        },
    }
    recall = Mock(return_value={"results": [recalled_hit]})
    reflect = Mock(return_value={"text": "Prior rerouting reduced delay at higher freight cost."})
    model_payload = _generated_recommendation(["memory-1"])
    model_call = Mock(
        return_value=SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=json.dumps(model_payload))
                )
            ]
        )
    )
    monkeypatch.setattr(decisions, "build_scenario", lambda *args: SCENARIO)
    monkeypatch.setattr(decisions.memory_service, "recall", recall)
    monkeypatch.setattr(decisions.memory_service, "reflect", reflect)
    monkeypatch.setattr(AgentService, "_call_model", lambda self, *args, **kwargs: model_call(*args, **kwargs))

    response = decisions.decision_recommendation(incident.id, context, db)
    report = response["data"]

    recall.assert_called_once()
    assert recall.call_args.args[1] is context.organization
    reflect.assert_called_once()
    assert reflect.call_args.args[1] is context.organization
    assert "Northstar Components" in recall.call_args.kwargs["query"]
    assert "Shipment Disruption" in recall.call_args.kwargs["query"]
    assert "control board" in recall.call_args.kwargs["query"]
    assert "historical recovery outcomes successful and unsuccessful strategies lessons learned" in recall.call_args.kwargs["query"]
    model_call.assert_called_once()
    model_prompt = json.loads(model_call.call_args.args[0][1]["content"])
    assert model_prompt["retrieved_memories"][0] == {
        "id": "memory-1",
        "text": "A previous port reroute reduced delay by three days.",
        "outcome": "Successful",
        "previous_strategy": "reroute",
        "verified": True,
        "source_type": "verified_business_fact",
        "confidence": 0.9,
    }
    assert model_prompt["hindsight_reflection"] == "Prior rerouting reduced delay at higher freight cost."
    assert report["aiRecommendation"]["status"] == "generated"
    assert report["aiRecommendation"]["strategyKey"] == "reroute"
    assert report["historicalEvidence"][0]["outcome"] == "Successful"
    assert report["memoryStatus"] == "available"
    assert report["reflectionStatus"] == "used"
    assert report["memoryComparison"]["memoryFreeStrategyKey"] == "wait"
    assert report["memoryComparison"]["memoryInformedStrategyKey"] == "reroute"


def test_decision_report_skips_reflect_without_memories_and_uses_baseline_on_groq_failure(monkeypatch):
    db, context, incident = _route_context()
    recall = Mock(return_value={"results": []})
    reflect = Mock()
    monkeypatch.setattr(decisions, "build_scenario", lambda *args: SCENARIO)
    monkeypatch.setattr(decisions.memory_service, "recall", recall)
    monkeypatch.setattr(decisions.memory_service, "reflect", reflect)
    monkeypatch.setattr(
        AgentService,
        "generate_decision_recommendation",
        Mock(side_effect=AgentUnavailable("provider unavailable")),
    )

    report = decisions.decision_recommendation(incident.id, context, db)["data"]

    recall.assert_called_once()
    reflect.assert_not_called()
    assert report["memoryStatus"] == "empty"
    assert report["reflectionStatus"] == "not_needed"
    assert report["aiRecommendation"]["status"] == "fallback"
    assert report["aiRecommendation"]["strategyKey"] == "wait"
    assert report["aiRecommendation"]["evidenceStrength"] == "none"


def test_decision_report_continues_without_hindsight(monkeypatch):
    db, context, incident = _route_context()
    recall = Mock(side_effect=HindsightUnavailable("unavailable"))
    reflect = Mock()
    generated = Mock(return_value=_generated_recommendation())
    monkeypatch.setattr(decisions, "build_scenario", lambda *args: SCENARIO)
    monkeypatch.setattr(decisions.memory_service, "recall", recall)
    monkeypatch.setattr(decisions.memory_service, "reflect", reflect)
    monkeypatch.setattr(AgentService, "generate_decision_recommendation", lambda self, **kwargs: generated(**kwargs))

    report = decisions.decision_recommendation(incident.id, context, db)["data"]

    assert report["memoryStatus"] == "unavailable"
    assert report["aiRecommendation"]["status"] == "generated"
    assert generated.call_args.kwargs["historical_evidence"] == []
    assert generated.call_args.kwargs["reflection"] is None
    reflect.assert_not_called()


def test_decision_report_continues_when_reflection_fails(monkeypatch):
    db, context, incident = _route_context()
    hit = {"id": "hit-1", "document_id": "memory-1", "text": "Retrieved lesson."}
    monkeypatch.setattr(decisions, "build_scenario", lambda *args: SCENARIO)
    monkeypatch.setattr(decisions.memory_service, "recall", Mock(return_value={"results": [hit]}))
    monkeypatch.setattr(decisions.memory_service, "reflect", Mock(side_effect=HindsightUnavailable("unavailable")))
    generated = Mock(return_value=_generated_recommendation(["memory-1"]))
    monkeypatch.setattr(AgentService, "generate_decision_recommendation", lambda self, **kwargs: generated(**kwargs))

    report = decisions.decision_recommendation(incident.id, context, db)["data"]

    assert report["reflectionStatus"] == "unavailable"
    assert report["aiRecommendation"]["status"] == "generated"
    assert generated.call_args.kwargs["reflection"] is None


@pytest.mark.parametrize("successful", [True, False])
def test_outcome_feedback_retains_success_and_failure(monkeypatch, successful):
    db, context, incident = _route_context()
    db.scalar = Mock(side_effect=[incident, SimpleNamespace(name="Northstar Components")])
    db.scalars = Mock(return_value=SimpleNamespace(all=lambda: []))
    db.add = Mock()
    db.flush = Mock()
    db.commit = Mock()
    db.refresh = Mock()
    retain = Mock(return_value={"status": "success"})
    monkeypatch.setattr(decisions.memory_service, "retain", retain)
    monkeypatch.setattr(decisions, "audit", Mock())

    payload = decisions.OutcomeFeedbackCreate(
        incidentId=incident.id,
        strategyKey="reroute",
        actualAdditionalCost=120,
        actualDeliveryDelayDays=1,
        actualInventoryShortage=2,
        ordersAffected=3,
        successful=successful,
        lessonsLearned="Route rerouting reduced the delay.",
        additionalNotes="Supplier confirmed capacity.",
    )
    response = decisions.record_outcome_feedback(payload, context, db)

    assert response["data"]["demo"] is False
    assert db.commit.call_count >= 1
    retain.assert_called_once()
    assert retain.call_args.args[1] is context.organization
    assert retain.call_args.kwargs["category"] == "outcome"
    assert retain.call_args.kwargs["source_type"] == "user_reported_fact"
    assert retain.call_args.kwargs["confidence"] == 0.5
    assert retain.call_args.kwargs["metadata"]["successful"] is successful
    assert retain.call_args.kwargs["metadata"]["product_component"] == incident.product_component
    assert retain.call_args.kwargs["metadata"]["expected_delay_days"] == incident.expected_delay_days
    assert f"Successful={successful}" in retain.call_args.kwargs["content"]
    assert "Port closure" in retain.call_args.kwargs["content"]
    assert incident.product_component in retain.call_args.kwargs["content"]
    assert incident.description in retain.call_args.kwargs["content"]


def test_outcome_feedback_remains_saved_when_hindsight_retain_fails(monkeypatch):
    db, context, incident = _route_context()
    db.scalar = Mock(side_effect=[incident, SimpleNamespace(name="Northstar Components")])
    db.scalars = Mock(return_value=SimpleNamespace(all=lambda: []))
    db.add = Mock()
    db.flush = Mock()
    db.commit = Mock()
    db.refresh = Mock()
    monkeypatch.setattr(decisions.memory_service, "retain", Mock(side_effect=HindsightUnavailable("unavailable")))
    monkeypatch.setattr(decisions, "audit", Mock())
    payload = decisions.OutcomeFeedbackCreate(
        incidentId=incident.id,
        strategyKey="reroute",
        actualAdditionalCost=120,
        actualDeliveryDelayDays=1,
        actualInventoryShortage=2,
        ordersAffected=3,
        successful=False,
        lessonsLearned="Rerouting did not resolve the shortage.",
        additionalNotes="",
    )

    response = decisions.record_outcome_feedback(payload, context, db)

    assert db.commit.call_count >= 1
    assert "Hindsight retention is currently unavailable" in response["data"]["message"]
