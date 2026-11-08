import uuid

import pytest
from types import SimpleNamespace
from unittest.mock import Mock
from pydantic import ValidationError

from app.api import crises as crises_api
from app.api.common import inventory_for_component
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


@pytest.mark.parametrize(
    ("crisis_type", "extra_fields"),
    [
        ("Supplier Failure", {"expectedDelayDays": 3}),
        ("Inventory Shortage", {"availableInventoryQuantity": 0}),
    ],
)
def test_non_shipment_crises_can_be_reported_without_linked_orders(crisis_type, extra_fields) -> None:
    report = {
        "crisisType": crisis_type,
        "incidentTitle": "Standalone supplier issue",
        "description": "A supplier or inventory issue has been identified.",
        "supplierId": "supplier-id",
        "shipmentId": None,
        "productComponent": "Control board",
        "origin": None,
        "destination": None,
        "expectedDelayDays": None,
        "availableInventoryQuantity": None,
        "affectedOrders": 0,
        "urgency": "High",
        "incidentDate": "2026-11-08",
        **extra_fields,
    }

    assert CrisisReportCreate.model_validate(report).shipment_id is None


def test_crisis_persists_tenant_linked_order_product(monkeypatch) -> None:
    organization_id = uuid.uuid4()
    supplier = SimpleNamespace(id=uuid.uuid4(), organization_id=organization_id)
    order = SimpleNamespace(
        id=uuid.uuid4(),
        organization_id=organization_id,
        supplier_id=supplier.id,
        product="MCU-1000 microcontrollers",
    )
    added = []
    db = SimpleNamespace(
        get=Mock(return_value=supplier),
        scalar=Mock(side_effect=[order, None, None]),
        add=Mock(side_effect=added.append),
        flush=Mock(),
        commit=Mock(),
        refresh=Mock(),
    )
    context = SimpleNamespace(
        organization=SimpleNamespace(id=organization_id),
        user=SimpleNamespace(id=uuid.uuid4()),
    )
    payload = CrisisReportCreate(
        crisisType="Shipment Disruption",
        incidentTitle="Port delay",
        description="A port closure delayed an existing shipment.",
        supplierId=str(supplier.id),
        shipmentId="121",
        productComponent="Incorrect free-text product",
        origin="Port A",
        destination="Warehouse B",
        expectedDelayDays=5,
        availableInventoryQuantity=None,
        affectedOrders=2,
        urgency="High",
        incidentDate="2026-11-08",
    )
    monkeypatch.setattr(crises_api, "audit", Mock())

    response = crises_api.create_crisis(payload, context, db)

    incident = added[0]
    assert response["data"]["incidentId"] == str(incident.id)
    assert incident.organization_id == organization_id
    assert incident.order_id == order.id
    assert incident.supplier_id == supplier.id
    assert incident.product_component == order.product
    db.commit.assert_called_once()


def test_inventory_matcher_resolves_sku_inside_order_product_and_scopes_tenant() -> None:
    organization_id = uuid.uuid4()
    supplier_id = uuid.uuid4()
    matching = SimpleNamespace(
        name="MCU-1000 microcontroller",
        sku="MCU-1000",
        supplier_id=supplier_id,
    )
    unrelated = SimpleNamespace(name="PCB-220 circuit board", sku="PCB-220", supplier_id=supplier_id)
    db = SimpleNamespace(scalars=Mock(return_value=SimpleNamespace(all=lambda: [matching, unrelated])))

    result = inventory_for_component(db, organization_id, supplier_id, "MCU-1000 microcontrollers")

    assert result == [matching]
    statement = db.scalars.call_args.args[0]
    assert organization_id in statement.compile().params.values()
    assert supplier_id in statement.compile().params.values()


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
