from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import Mock

from app.api.common import inventory_for_component


class InventorySession:
    def __init__(self, items):
        self.items = items
        self.statement = None

    def scalars(self, statement):
        self.statement = statement
        params = statement.compile().params
        organization_id = next(
            value for key, value in params.items() if key.startswith("organization_id")
        )
        supplier_id = next(
            (value for key, value in params.items() if key.startswith("supplier_id")),
            None,
        )
        matching = [
            item
            for item in self.items
            if item.organization_id == organization_id
            and (supplier_id is None or item.supplier_id == supplier_id)
        ]
        return SimpleNamespace(all=lambda: matching)


def _item(name: str, sku: str, organization_id=None, supplier_id=None):
    return SimpleNamespace(
        name=name,
        sku=sku,
        organization_id=organization_id,
        supplier_id=supplier_id,
    )


def test_inventory_lookup_matches_exact_sku():
    organization_id = uuid.uuid4()
    item = _item("Microcontroller", "MCU-1000", organization_id)
    db = InventorySession([item])

    result = inventory_for_component(db, organization_id, None, "MCU-1000")

    assert result.status == "matched"
    assert result.items == (item,)
    assert result.detail == "Matched exact SKU MCU-1000."


def test_inventory_lookup_extracts_sku_embedded_in_product_description():
    organization_id = uuid.uuid4()
    item = _item("Microcontroller", "MCU-1000", organization_id)
    db = InventorySession([item])

    result = inventory_for_component(
        db, organization_id, None, "Critical control board using MCU-1000 components"
    )

    assert result.status == "matched"
    assert result.items == (item,)


def test_inventory_lookup_does_not_match_similar_sku_prefixes():
    organization_id = uuid.uuid4()
    short_sku = _item("Short part", "ABC123", organization_id)
    long_sku = _item("Long part", "ABC1234", organization_id)
    db = InventorySession([short_sku, long_sku])

    short_result = inventory_for_component(db, organization_id, None, "Assembly ABC123")
    long_result = inventory_for_component(db, organization_id, None, "Assembly ABC1234")

    assert short_result.items == (short_sku,)
    assert long_result.items == (long_sku,)


def test_inventory_lookup_accepts_only_an_exact_canonical_product_name():
    organization_id = uuid.uuid4()
    item = _item("Control Board", "CB-7", organization_id)
    db = InventorySession([item])

    result = inventory_for_component(db, organization_id, None, "control-board")
    partial_result = inventory_for_component(db, organization_id, None, "Control Board Assembly")

    assert result.status == "matched"
    assert result.items == (item,)
    assert partial_result.status == "unmapped"
    assert not partial_result.items


def test_inventory_lookup_marks_duplicate_product_names_ambiguous():
    organization_id = uuid.uuid4()
    first = _item("Control Board", "CB-7", organization_id)
    second = _item("Control Board", "CB-8", organization_id)
    db = InventorySession([first, second])

    result = inventory_for_component(db, organization_id, None, "Control Board")

    assert result.status == "ambiguous"
    assert not result.items
    assert "provide a SKU" in result.detail


def test_inventory_lookup_reports_missing_mapping_instead_of_returning_zero_matches():
    organization_id = uuid.uuid4()
    item = _item("Control Board", "CB-7", organization_id)
    db = InventorySession([item])

    result = inventory_for_component(db, organization_id, None, "Unknown component")

    assert result.status == "unmapped"
    assert not result.items
    assert "No inventory record matched" in result.detail


def test_inventory_lookup_preserves_organization_and_supplier_filters():
    organization_id = uuid.uuid4()
    other_organization_id = uuid.uuid4()
    supplier_id = uuid.uuid4()
    other_supplier_id = uuid.uuid4()
    matching = _item("Controller", "CTRL-1", organization_id, supplier_id)
    wrong_supplier = _item("Controller", "CTRL-2", organization_id, other_supplier_id)
    wrong_organization = _item("Controller", "CTRL-3", other_organization_id, supplier_id)
    db = InventorySession([matching, wrong_supplier, wrong_organization])

    result = inventory_for_component(db, organization_id, supplier_id, "CTRL-1")

    assert result.status == "matched"
    assert result.items == (matching,)
    compiled = db.statement.compile()
    assert organization_id in compiled.params.values()
    assert supplier_id in compiled.params.values()


def test_inventory_lookup_marks_multiple_matching_skus_ambiguous():
    organization_id = uuid.uuid4()
    first = _item("Control Board", "CB-7", organization_id)
    second = _item("Power Board", "PB-2", organization_id)
    db = InventorySession([first, second])

    result = inventory_for_component(db, organization_id, None, "CB-7 plus PB-2")

    assert result.status == "ambiguous"
    assert not result.items


def test_blank_component_does_not_query_inventory():
    db = SimpleNamespace(scalars=Mock())

    result = inventory_for_component(db, uuid.uuid4(), None, "  ")

    assert result.status == "unmapped"
    db.scalars.assert_not_called()
