import pytest
from pydantic import ValidationError

from app.main import app
from app.schemas_incidents import CrisisReportCreate, DecisionActionCreate, OutcomeFeedbackCreate


def test_required_frontend_routes_are_registered_at_contract_paths() -> None:
    routes = {
        (method.upper(), path)
        for path, operations in app.openapi()["paths"].items()
        for method in operations
    }

    required = {
        ("POST", "/api/v1/auth/demo-login"),
        ("GET", "/api/v1/dashboard"),
        ("GET", "/api/crises/form-options"),
        ("POST", "/api/crises"),
        ("GET", "/api/impacts/incidents"),
        ("GET", "/api/impacts/incidents/{incident_id}"),
        ("GET", "/api/recovery-simulations/incidents"),
        ("GET", "/api/recovery-simulations/incidents/{incident_id}"),
        ("POST", "/api/recovery-simulations/confirmations"),
        ("GET", "/api/decisions/incidents"),
        ("GET", "/api/decisions/incidents/{incident_id}/recommendation"),
        ("POST", "/api/decisions/actions"),
        ("POST", "/api/decisions/outcomes"),
        ("GET", "/api/decision-replays/incidents"),
        ("GET", "/api/decision-replays/{incident_id}"),
        ("POST", "/api/decision-replays/{incident_id}/run"),
        ("GET", "/api/memories/overview"),
        ("GET", "/api/memories"),
        ("GET", "/api/memories/{memoryId}"),
    }
    assert required <= routes


def test_crisis_report_requires_shipment_fields_for_shipment_disruptions() -> None:
    report = {
        "crisisType": "Shipment Disruption",
        "incidentTitle": "Port closure",
        "description": "Port access is blocked and the shipment is delayed.",
        "supplierId": "supplier-id",
        "shipmentId": "PO-123",
        "productComponent": "control board",
        "origin": "Port A",
        "destination": "Warehouse B",
        "expectedDelayDays": 4,
        "availableInventoryQuantity": None,
        "affectedOrders": 2,
        "urgency": "High",
        "incidentDate": "2026-11-07",
    }
    assert CrisisReportCreate.model_validate(report).shipment_id == "PO-123"

    report["shipmentId"] = None
    with pytest.raises(ValidationError):
        CrisisReportCreate.model_validate(report)


def test_rejected_decision_requires_null_strategy_key() -> None:
    valid = DecisionActionCreate.model_validate(
        {
            "incidentId": "d02c66cf-06bc-44a7-a7f3-103c24c39b94",
            "action": "rejected",
            "strategyKey": None,
            "explanation": "",
        }
    )
    assert valid.strategy_key is None

    with pytest.raises(ValidationError):
        DecisionActionCreate.model_validate(
            {
                "incidentId": "d02c66cf-06bc-44a7-a7f3-103c24c39b94",
                "action": "rejected",
                "strategyKey": "wait",
                "explanation": "",
            }
        )


def test_outcome_payload_accepts_contract_fields_and_validates_numbers() -> None:
    payload = OutcomeFeedbackCreate.model_validate(
        {
            "incidentId": "d02c66cf-06bc-44a7-a7f3-103c24c39b94",
            "strategyKey": "reroute",
            "actualAdditionalCost": 125.5,
            "actualDeliveryDelayDays": 2,
            "actualInventoryShortage": 12,
            "ordersAffected": 3,
            "successful": True,
            "lessonsLearned": "Secure capacity before rerouting.",
            "additionalNotes": "",
        }
    )
    assert payload.actual_additional_cost == 125.5

    with pytest.raises(ValidationError):
        OutcomeFeedbackCreate.model_validate(
            {
                "incidentId": "d02c66cf-06bc-44a7-a7f3-103c24c39b94",
                "strategyKey": "reroute",
                "actualAdditionalCost": -1,
                "actualDeliveryDelayDays": 2,
                "actualInventoryShortage": 12,
                "ordersAffected": 3,
                "successful": True,
            }
        )
