"""Repeatable synthetic demonstration dataset.

Every row is flagged synthetic. The dataset intentionally contains good and bad
suppliers so that memory-driven recommendations can be evaluated.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import (
    Alert,
    DecisionOutcome,
    EvaluationResult,
    EvaluationRun,
    InventoryItem,
    InventoryMovement,
    Membership,
    MemoryOperationLog,
    MemoryRecord,
    Organization,
    ProcurementDecision,
    PurchaseOrder,
    QualityIncident,
    ScheduledAction,
    ShipmentEvent,
    Supplier,
    SupplierComplaint,
    User,
)
from ..security import hash_password
from . import memory as memory_service

logger = logging.getLogger("supplymind.seed")

DEMO_EMAIL = "demo@supplymind.local"
DEMO_PASSWORD = "SupplyMindDemo!23"
DEMO_ORG_NAME = "Northwind Industrial (Demo)"
DEMO_SLUG = "northwind-demo"


def _today() -> datetime:
    return datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)


def _at(days: int, hour: int = 12) -> datetime:
    return (_today() + timedelta(days=days)).replace(hour=hour)


SUPPLIER_SPECS = [
    {
        "key": "alpha",
        "name": "Alpha Components",
        "contact_name": "Wei Zhang",
        "contact_email": "wei.zhang@alpha-components.example",
        "contact_phone": "+86 21 5550 0101",
        "city": "Shanghai",
        "country": "China",
        "categories": ["electronic components", "PCBs", "connectors"],
        "promised_lead_days": 5,
        "notes": "Low-cost source. Repeated delivery slippage and solder-quality complaints in the last year.",
    },
    {
        "key": "meridian",
        "name": "Meridian Electronics",
        "contact_name": "Priya Nair",
        "contact_email": "priya.nair@meridian-electronics.example",
        "contact_phone": "+65 6550 2200",
        "city": "Singapore",
        "country": "Singapore",
        "categories": ["electronic components", "microcontrollers"],
        "promised_lead_days": 6,
        "notes": "Preferred urgent-order source. Consistent on-time performance and clear communication.",
    },
    {
        "key": "nordic",
        "name": "Nordic Parts",
        "contact_name": "Erik Lund",
        "contact_email": "erik.lund@nordic-parts.example",
        "contact_phone": "+46 31 555 0300",
        "city": "Gothenburg",
        "country": "Sweden",
        "categories": ["precision components", "sensors"],
        "promised_lead_days": 8,
        "notes": "Premium-priced, highly reliable precision components supplier.",
    },
    {
        "key": "vertex",
        "name": "Shenzhen Vertex",
        "contact_name": "Lina Chen",
        "contact_email": "lina.chen@vertex.example",
        "contact_phone": "+86 755 5550 0404",
        "city": "Shenzhen",
        "country": "China",
        "categories": ["connectors", "cables", "power supplies"],
        "promised_lead_days": 7,
        "notes": "Mixed record: acceptable lead times but recurring connector quality defects.",
    },
    {
        "key": "pacific",
        "name": "Pacific Supply Co",
        "contact_name": "Marco Ruiz",
        "contact_email": "marco.ruiz@pacific-supply.example",
        "contact_phone": "+1 562 555 0505",
        "city": "Long Beach",
        "country": "United States",
        "categories": ["packaging", "industrial components"],
        "promised_lead_days": 10,
        "notes": "Port congestion and customs holds have repeatedly affected west-coast shipments.",
    },
]

# (number, supplier_key, product, qty, promised_lead, status, delay_days or None,
#  order_days_ago, priority, destination, mode, financial_impact)
ORDER_SPECS = [
    ("101", "alpha", "MCU-1000 microcontrollers", 1000, 5, "delivered", 10, 160, "high", "Chicago DC", "sea", 48000),
    ("102", "alpha", "PCB-220 circuit boards", 400, 7, "delivered", 5, 150, "normal", "Chicago DC", "sea", 22000),
    ("103", "alpha", "CON-330 connectors", 2500, 5, "delivered", 8, 138, "high", "Dallas DC", "air", 31000),
    ("104", "alpha", "PSU-12 power supplies", 300, 6, "delivered", 0, 120, "normal", "Dallas DC", "sea", 18000),
    ("105", "meridian", "MCU-1000 microcontrollers", 1200, 6, "delivered", 0, 145, "critical", "Chicago DC", "air", 62000),
    ("106", "meridian", "SEN-88 sensors", 800, 5, "delivered", 0, 130, "high", "Chicago DC", "air", 34000),
    ("107", "meridian", "CON-330 connectors", 3000, 7, "delivered", 1, 115, "normal", "Dallas DC", "sea", 27000),
    ("108", "meridian", "PCB-220 circuit boards", 500, 6, "delivered", 0, 98, "high", "Dallas DC", "air", 25000),
    ("109", "meridian", "MCU-1000 microcontrollers", 900, 6, "delivered", 0, 70, "critical", "Chicago DC", "air", 55000),
    ("110", "nordic", "SEN-88 precision sensors", 600, 8, "delivered", 0, 140, "normal", "Chicago DC", "air", 41000),
    ("111", "nordic", "BRG-44 bearings", 1500, 10, "delivered", 0, 128, "normal", "Dallas DC", "sea", 20000),
    ("112", "nordic", "SEN-88 precision sensors", 750, 8, "delivered", 2, 105, "high", "Chicago DC", "air", 38000),
    ("113", "nordic", "BRG-44 bearings", 2000, 10, "delivered", 0, 82, "normal", "Dallas DC", "sea", 24000),
    ("114", "vertex", "CON-330 connectors", 5000, 7, "delivered", 7, 135, "normal", "Dallas DC", "sea", 19000),
    ("115", "vertex", "CBL-77 cable assemblies", 1200, 6, "delivered", 4, 112, "normal", "Dallas DC", "sea", 16000),
    ("116", "vertex", "PSU-12 power supplies", 450, 7, "delivered", 8, 90, "high", "Chicago DC", "sea", 21000),
    ("117", "vertex", "CON-330 connectors", 3500, 7, "delivered", 6, 60, "normal", "Dallas DC", "air", 23000),
    ("118", "pacific", "PKG-90 industrial packaging", 10000, 10, "delivered", 9, 125, "normal", "Long Beach DC", "sea", 15000),
    ("119", "pacific", "IND-55 industrial components", 700, 10, "delivered", 6, 95, "high", "Long Beach DC", "sea", 29000),
    ("120", "pacific", "PKG-90 industrial packaging", 12000, 10, "delivered", 0, 55, "normal", "Long Beach DC", "sea", 17000),
    # open / future orders
    ("121", "alpha", "MCU-1000 microcontrollers", 1000, 5, "in_transit", None, 3, "critical", "Chicago DC", "sea", 52000),
    ("122", "meridian", "SEN-88 sensors", 900, 6, "confirmed", None, 1, "high", "Chicago DC", "air", 36000),
    ("123", "vertex", "CON-330 connectors", 4000, 7, "processing", None, 4, "normal", "Dallas DC", "sea", 21000),
    ("124", "pacific", "IND-55 industrial components", 800, 10, "delayed", None, 18, "high", "Long Beach DC", "sea", 33000),
    ("125", "nordic", "SEN-88 precision sensors", 500, 8, "confirmed", None, 2, "normal", "Chicago DC", "air", 30000),
]


def _get_or_create_org(db: Session) -> Organization:
    org = db.scalar(select(Organization).where(Organization.slug == DEMO_SLUG))
    if org:
        return org
    bank_id = f"sm_{uuid.uuid4().hex[:16]}"
    org = Organization(
        name=DEMO_ORG_NAME,
        slug=DEMO_SLUG,
        memory_bank_id=bank_id,
        is_demo=True,
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def _get_or_create_demo_user(db: Session, org: Organization) -> User:
    user = db.scalar(select(User).where(User.email == DEMO_EMAIL))
    if user:
        return user
    user = User(
        organization_id=org.id,
        email=DEMO_EMAIL,
        full_name="Dana Whitfield (Demo Procurement Manager)",
        password_hash=hash_password(DEMO_PASSWORD),
        role="procurement_manager",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.add(Membership(organization_id=org.id, user_id=user.id, role="owner"))
    db.commit()
    return user


def is_seeded(db: Session, org: Organization) -> bool:
    count = db.scalar(select(PurchaseOrder).where(PurchaseOrder.organization_id == org.id))
    return count is not None


def demo_exists(db: Session) -> bool:
    """True when the demo organization and user already exist."""
    org = db.scalar(select(Organization).where(Organization.slug == DEMO_SLUG))
    if org is None:
        return False
    user = db.scalar(select(User).where(func.lower(User.email) == DEMO_EMAIL))
    return user is not None


def _wipe_synthetic(db: Session, org: Organization) -> None:
    """Delete only synthetic demo rows for the demo organization."""
    from sqlalchemy import delete

    for model in (
        EvaluationResult,
        EvaluationRun,
        MemoryOperationLog,
        MemoryRecord,
        Alert,
        ScheduledAction,
        DecisionOutcome,
        ProcurementDecision,
        InventoryMovement,
        InventoryItem,
        QualityIncident,
        SupplierComplaint,
        ShipmentEvent,
        PurchaseOrder,
        Supplier,
    ):
        db.execute(delete(model).where(model.organization_id == org.id))
    db.commit()


def seed_business_data(db: Session, org: Organization, force: bool = False) -> dict:
    if force:
        _wipe_synthetic(db, org)
    elif is_seeded(db, org):
        return {"seeded": False, "reason": "dataset already present", "organization_id": str(org.id)}

    today = _today()
    suppliers: dict[str, Supplier] = {}
    for spec in SUPPLIER_SPECS:
        s = Supplier(
            organization_id=org.id,
            name=spec["name"],
            contact_name=spec["contact_name"],
            contact_email=spec["contact_email"],
            contact_phone=spec["contact_phone"],
            city=spec["city"],
            country=spec["country"],
            categories=spec["categories"],
            promised_lead_days=spec["promised_lead_days"],
            notes=spec["notes"],
            status="active",
            synthetic=True,
        )
        db.add(s)
        suppliers[spec["key"]] = s
    db.commit()
    for s in suppliers.values():
        db.refresh(s)

    orders: dict[str, PurchaseOrder] = {}
    for number, skey, product, qty, lead, status, delay, days_ago, priority, destination, mode, impact in ORDER_SPECS:
        order_date = today - timedelta(days=days_ago)
        promised = order_date + timedelta(days=lead)
        actual = None
        estimated = promised
        if status == "delivered":
            actual = promised + timedelta(days=delay or 0)
        elif status == "delayed":
            estimated = promised + timedelta(days=12)
        else:
            estimated = promised + timedelta(days=2)

        special_tracking = {"101": "SEA-ROT-101", "105": "AIR-SIN-105", "118": "SEA-LGB-118", "121": "SEA-SHA-121"}
        order = PurchaseOrder(
            organization_id=org.id,
            supplier_id=suppliers[skey].id,
            order_number=number,
            product=product,
            quantity=qty,
            order_date=order_date,
            promised_date=promised,
            estimated_arrival=estimated,
            actual_arrival=actual,
            status=status,
            priority=priority,
            destination=destination,
            transport_mode=mode,
            tracking_reference=special_tracking.get(number, f"TRK-{number}"),
            financial_impact=float(impact),
            notes="Synthetic demonstration order.",
            synthetic=True,
        )
        db.add(order)
        orders[number] = order
    db.commit()
    for o in orders.values():
        db.refresh(o)

    # Shipment events (including transportation disruptions).
    event_specs = [
        ("101", "dispatched", -24, "Shanghai port", "Container loaded at Shanghai port."),
        ("101", "customs_hold", -18, "Rotterdam port", "Customs hold delayed the vessel for six days."),
        ("101", "delivered", -10, "Chicago DC", "Delivered ten days after the promised date."),
        ("102", "delay", -11, "Singapore transshipment", "Missed connection added five days."),
        ("105", "delivered", -70, "Chicago DC", "Delivered on the promised date via air freight."),
        ("115", "incident", -30, "Dallas DC", "Two cartons arrived with damaged connectors."),
        ("118", "delay", -35, "Long Beach port", "Port congestion delayed unloading by nine days."),
        ("119", "customs_hold", -25, "Long Beach port", "Customs inspection held the shipment for six days."),
        ("121", "dispatched", -3, "Shanghai port", "Container departed Shanghai; no further update from supplier."),
        ("124", "delay", -5, "Long Beach port", "Vessel waiting offshore; ETA pushed by twelve days."),
    ]
    for number, etype, days, location, description in event_specs:
        db.add(
            ShipmentEvent(
                organization_id=org.id,
                order_id=orders[number].id,
                event_type=etype,
                event_date=_at(days),
                location=location,
                description=description,
                source="synthetic_carrier_feed",
                synthetic=True,
            )
        )

    # Complaints and quality incidents.
    complaint_specs = [
        ("alpha", "101", "quality", "high", "Solder defects found in 8% of the MCU batch; rework required.", -95),
        ("alpha", "102", "communication", "medium", "No status updates for 12 days; escalation required.", -100),
        ("alpha", "103", "transportation", "high", "Air shipment missed the booked flight twice.", -80),
        ("alpha", "104", "communication", "low", "Slow response to confirmation requests.", -60),
        ("vertex", "114", "quality", "high", "Connector pins bent on arrival; 12% rejection rate.", -85),
        ("vertex", "116", "quality", "medium", "Power supplies failed incoming inspection.", -55),
        ("vertex", "117", "communication", "medium", "Supplier did not confirm the revised dispatch date.", -40),
        ("pacific", "118", "transportation", "high", "Port congestion caused a nine-day delay.", -70),
        ("pacific", "119", "transportation", "medium", "Customs hold without proactive notification.", -45),
        ("meridian", "107", "communication", "low", "One status report arrived a day late.", -50),
    ]
    for skey, number, ctype, severity, description, days in complaint_specs:
        db.add(
            SupplierComplaint(
                organization_id=org.id,
                supplier_id=suppliers[skey].id,
                order_id=orders[number].id,
                complaint_type=ctype,
                severity=severity,
                description=description,
                reported_date=_at(days),
                status="closed",
                synthetic=True,
            )
        )

    incident_specs = [
        ("alpha", "101", "high", "8% solder-defect rate required rework before production.", -95),
        ("vertex", "114", "high", "12% connector rejection at incoming inspection.", -85),
        ("vertex", "116", "medium", "Power supply batch failed load testing.", -55),
    ]
    for skey, number, severity, description, days in incident_specs:
        db.add(
            QualityIncident(
                organization_id=org.id,
                supplier_id=suppliers[skey].id,
                order_id=orders[number].id,
                description=description,
                severity=severity,
                occurred_at=_at(days),
                resolved=True,
                synthetic=True,
            )
        )

    # Previous procurement decisions and outcomes.
    prior_decisions = [
        (
            "Which supplier should we use for the urgent 1,000 microcontroller order?",
            "alpha",
            "Chose Alpha Components for the lowest unit price despite known delays.",
            "proposed",
            False,
            "Alpha delivered 10 days late; production line ran overtime for three shifts.",
            -60,
        ),
        (
            "Should we switch the microcontroller order to Meridian Electronics?",
            "meridian",
            "Switched to Meridian Electronics after Alpha missed two consecutive delivery windows.",
            "approved",
            True,
            "Meridian delivered on time; overtime cost avoided and line schedule held.",
            -50,
        ),
        (
            "Which supplier should provide connectors for the Q3 build?",
            "vertex",
            "Selected Shenzhen Vertex on price; quality inspection was added as a mitigation.",
            "approved",
            False,
            "12% of connectors were rejected; inspection and rework cost exceeded the price saving.",
            -35,
        ),
    ]
    for question, skey, rationale, status, success, outcome, days in prior_decisions:
        decision = ProcurementDecision(
            organization_id=org.id,
            question=question,
            recommended_supplier_id=suppliers[skey].id,
            decision="approved" if status == "approved" else "proposed",
            rationale=rationale,
            evidence={"source": "synthetic historical decision"},
            status=status,
            synthetic=True,
        )
        db.add(decision)
        db.commit()
        db.refresh(decision)
        db.add(
            DecisionOutcome(
                organization_id=org.id,
                decision_id=decision.id,
                outcome=outcome,
                success=success,
                notes="Synthetic outcome recorded for demonstration.",
                recorded_at=_at(days),
                synthetic=True,
            )
        )

    # Inventory.
    inventory_specs = [
        ("MCU-1000", "MCU-1000 microcontroller", "electronic components", 420, 500, "critical", 18.5, "alpha"),
        ("CON-330", "CON-330 connector", "connectors", 1800, 1500, "high", 2.4, "vertex"),
        ("PCB-220", "PCB-220 circuit board", "PCBs", 260, 300, "high", 9.1, "alpha"),
        ("SEN-88", "SEN-88 precision sensor", "sensors", 640, 400, "medium", 31.0, "nordic"),
        ("PKG-90", "PKG-90 packaging unit", "packaging", 5400, 3000, "low", 0.9, "pacific"),
    ]
    items = []
    for sku, name, cat, qty, reorder, criticality, cost, skey in inventory_specs:
        item = InventoryItem(
            organization_id=org.id,
            sku=sku,
            name=name,
            category=cat,
            quantity_on_hand=qty,
            reorder_point=reorder,
            criticality=criticality,
            unit_cost=cost,
            supplier_id=suppliers[skey].id,
            synthetic=True,
        )
        db.add(item)
        items.append(item)
    db.commit()
    for item in items:
        db.refresh(item)
        db.add(
            InventoryMovement(
                organization_id=org.id,
                item_id=item.id,
                movement_type="consumption",
                quantity=-120,
                reference="synthetic production draw",
                occurred_at=_at(-7),
                synthetic=True,
            )
        )

    # A couple of pre-existing alerts for a realistic dashboard.
    db.add(
        Alert(
            organization_id=org.id,
            order_id=orders["124"].id,
            supplier_id=suppliers["pacific"].id,
            alert_type="overdue_order",
            severity="high",
            title="Overdue order: 124",
            message="Pacific Supply Co is past the promised date; port congestion is blocking delivery.",
            status="open",
            due_at=orders["124"].promised_date,
            dedupe_key="seed:alert:124",
            synthetic=True,
        )
    )
    db.add(
        Alert(
            organization_id=org.id,
            order_id=orders["121"].id,
            supplier_id=suppliers["alpha"].id,
            alert_type="supplier_confirmation_reminder",
            severity="medium",
            title="Confirm urgent order 121 with Alpha Components",
            message="Historical average delay is 7.7 days. Request a dated shipment confirmation now.",
            status="open",
            due_at=orders["121"].promised_date,
            dedupe_key="seed:alert:121",
            synthetic=True,
        )
    )
    db.commit()

    return {
        "seeded": True,
        "organization_id": str(org.id),
        "suppliers": len(suppliers),
        "orders": len(orders),
        "delivered_orders": len([o for o in orders.values() if o.status == "delivered"]),
        "complaints": len(complaint_specs),
        "synthetic": True,
    }


# 20 meaningful organizational experiences used by the Memory Learning Lab.
LAB_EXPERIENCES = [
    ("101", "alpha", "episodic", "Order 101 from Alpha Components was promised in 5 days but delivered in 15 days, a 10-day delay. Customs held the shipment at Rotterdam for six days.", -150),
    ("102", "alpha", "episodic", "Order 102 from Alpha Components was promised in 7 days but delivered in 12 days. The supplier missed a transshipment connection in Singapore.", -143),
    ("103", "alpha", "episodic", "Order 103 from Alpha Components was promised in 5 days but delivered in 13 days. The air shipment missed two booked flights.", -130),
    ("104", "alpha", "episodic", "Order 104 from Alpha Components arrived on time after 6 days, showing the supplier can occasionally meet a standard lead time.", -114),
    ("alpha", None, "semantic", "Alpha Components has a repeated pattern of 5-10 day delivery slippage on urgent electronic component orders, and frequently does not send proactive status updates.", -110),
    ("101", "alpha", "outcome", "Alpha Components delivered 8% of MCU-1000 microcontrollers with solder defects on order 101. Incoming inspection rejected the affected units and production required rework.", -95),
    ("102", "alpha", "episodic", "Alpha Components provided no status update for 12 days on order 102 until procurement escalated to the account manager.", -92),
    ("105", "meridian", "episodic", "Order 105 from Meridian Electronics was promised in 6 days and delivered on the promised date using air freight, despite critical priority.", -139),
    ("106", "meridian", "episodic", "Order 106 from Meridian Electronics was delivered on time in 5 days with complete advance shipping notices.", -124),
    ("109", "meridian", "outcome", "Choosing Meridian Electronics for the urgent microcontroller order 109 avoided production overtime; the order arrived on time and the line schedule held.", -64),
    ("107", "meridian", "episodic", "Order 107 from Meridian Electronics was one day late but the supplier communicated the revised ETA two days in advance.", -109),
    ("meridian", None, "semantic", "Meridian Electronics is the most reliable source for urgent electronic components: on-time delivery, clear communication and no quality incidents in the last 12 months.", -60),
    ("110", "nordic", "episodic", "Nordic Parts delivered order 110 of precision sensors on the promised date with full documentation.", -134),
    ("112", "nordic", "episodic", "Order 112 from Nordic Parts arrived two days late but quality was fully within specification.", -99),
    ("114", "vertex", "episodic", "Shenzhen Vertex delivered order 114 seven days late and 12% of connector pins were bent on arrival, causing an incoming-inspection rejection.", -129),
    ("116", "vertex", "outcome", "Selecting Shenzhen Vertex for power supplies on price led to failed load testing on order 116; rework and expedited replacement cost more than the price saving.", -84),
    ("118", "pacific", "episodic", "Pacific Supply Co order 118 was nine days late because of port congestion at Long Beach.", -119),
    ("119", "pacific", "episodic", "Pacific Supply Co order 119 was held six days in customs without proactive notification.", -89),
    ("alpha", "alpha", "decision", "Previous procurement decision: Alpha Components was selected for the urgent 1,000 microcontroller order on price, despite known delays. The order arrived 10 days late and caused three shifts of overtime.", -60),
    (None, None, "preference", "Company procurement preference: for critical electronic components, prefer an on-time supplier with a verified record over the lowest price, and keep at least a 3-day delivery buffer.", -30),
]


def seed_memories(db: Session, org: Organization, experiences: list | None = None) -> dict:
    """Retain meaningful experiences in Hindsight (real SDK calls)."""
    memory_service.ensure_bank(org)
    experiences = experiences or LAB_EXPERIENCES
    suppliers = {s.name.lower(): s for s in db.scalars(select(Supplier).where(Supplier.organization_id == org.id)).all()}
    orders = {o.order_number: o for o in db.scalars(select(PurchaseOrder).where(PurchaseOrder.organization_id == org.id)).all()}
    retained = 0
    errors = 0
    details = []
    for idx, (order_number, supplier_key, category, content, days) in enumerate(experiences):
        supplier = suppliers.get(str(supplier_key).lower()) if supplier_key else None
        order = orders.get(order_number) if order_number else None
        try:
            result = memory_service.retain(
                db,
                org,
                content=content,
                category=category,
                source_type="verified_business_fact" if category != "preference" else "user_reported_fact",
                supplier_id=supplier.id if supplier else None,
                order_id=order.id if order else None,
                event_date=_at(days),
                context=f"{category} supply-chain experience",
                synthetic=True,
            )
            retained += 1
            details.append({"index": idx, "document_id": result["document_id"], "category": category})
        except Exception as exc:  # noqa: BLE001
            errors += 1
            details.append({"index": idx, "error": str(exc)[:300]})
    return {"retained": retained, "errors": errors, "total": len(experiences), "details": details}


def seed_demo(db: Session, force: bool = False, retain_memories: bool = True) -> dict:
    org = _get_or_create_org(db)
    _get_or_create_demo_user(db, org)
    result = seed_business_data(db, org, force=force)
    memory_result = None
    if retain_memories:
        existing = db.scalars(
            select(MemoryRecord).where(
                MemoryRecord.organization_id == org.id,
                MemoryRecord.synthetic.is_(True),
            )
        ).all()
        if force or len(existing) < len(LAB_EXPERIENCES):
            if existing:
                memory_service.reset_bank(db, org)
            memory_result = seed_memories(db, org)
    result["memory"] = memory_result
    result["demo_user"] = DEMO_EMAIL
    return result
