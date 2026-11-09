from types import SimpleNamespace
from uuid import uuid4

from app.api.common import inventory_for_component, resolve_inventory_for_component


class FilteringSession:
    def __init__(self, items, organization_id, supplier_id=None):
        self.items = items
        self.organization_id = organization_id
        self.supplier_id = supplier_id

    def scalars(self, _query):
        items = [item for item in self.items if item.organization_id == self.organization_id]
        if self.supplier_id is not None:
            items = [item for item in items if item.supplier_id == self.supplier_id]
        return SimpleNamespace(all=lambda: items)


def item(org, supplier, sku, name):
    return SimpleNamespace(organization_id=org, supplier_id=supplier, sku=sku, name=name)


def test_exact_and_embedded_sku_do_not_match_similar_skus():
    org = uuid4()
    supplier = uuid4()
    db = FilteringSession(
        [item(org, supplier, "ABC123", "Controller"), item(org, supplier, "ABC1234", "Controller Plus")],
        org,
        supplier,
    )

    assert [row.sku for row in inventory_for_component(db, org, supplier, "ABC123")] == ["ABC123"]
    assert [row.sku for row in inventory_for_component(db, org, supplier, "Urgent component ABC123")] == ["ABC123"]
    assert inventory_for_component(db, org, supplier, "ABC1234X") == []


def test_duplicate_names_are_ambiguous_and_wrong_tenant_or_supplier_is_excluded():
    org = uuid4()
    other_org = uuid4()
    supplier = uuid4()
    other_supplier = uuid4()
    db = FilteringSession(
        [
            item(org, supplier, "SKU-1", "Duplicate Name"),
            item(org, supplier, "SKU-2", "Duplicate Name"),
            item(org, other_supplier, "SKU-3", "Other Supplier"),
            item(other_org, supplier, "SKU-4", "Other Organization"),
        ],
        org,
        supplier,
    )

    result = resolve_inventory_for_component(db, org, supplier, "Duplicate Name")
    assert result.status == "ambiguous"
    assert result.items == ()
    assert resolve_inventory_for_component(db, org, supplier, "Other Supplier").status == "missing"


def test_missing_mapping_is_explicit():
    org = uuid4()
    db = FilteringSession([], org)
    result = resolve_inventory_for_component(db, org, None, "Unknown component")
    assert result.status == "missing"
    assert result.items == ()


def test_canonical_sku_collision_is_ambiguous():
    org = uuid4()
    supplier = uuid4()
    db = FilteringSession(
        [item(org, supplier, "ABC-123", "First"), item(org, supplier, "ABC123", "Second")],
        org,
        supplier,
    )

    result = resolve_inventory_for_component(db, org, supplier, "ABC123")
    assert result.status == "ambiguous"
    assert result.items == ()
