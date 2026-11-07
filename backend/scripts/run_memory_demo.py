from __future__ import annotations
import sys, os, uuid, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from app.db import SessionLocal
from app.models import Organization, User, Membership, Supplier, PurchaseOrder, SupplierComplaint
from app.security import hash_password
from app.services import memory as memory_service
from app.services.agent import AgentService
from app.services import metrics as metrics_service

db = SessionLocal()
org = db.scalar(select(Organization).where(Organization.name == "SUPPLYMIND DEMO"))
if org is None:
    org = Organization(name="SUPPLYMIND DEMO", slug="supplymind-demo", memory_bank_id=f"sm_{uuid.uuid4().hex[:16]}")
    db.add(org); db.commit(); db.refresh(org)
    memory_service.ensure_bank(org)
user = db.scalar(select(User).where(User.email == "demo@supplyminddemo.com"))
if user is None:
    user = User(organization_id=org.id, email="demo@supplyminddemo.com", full_name="Demo User", password_hash=hash_password("demo1234"), role="owner", is_active=True)
    db.add(user); db.commit(); db.refresh(user)
    db.add(Membership(organization_id=org.id, user_id=user.id, role="owner")); db.commit()

def get_supplier(name):
    return db.scalar(select(Supplier).where(Supplier.organization_id==org.id, Supplier.name==name))

alpha = get_supplier("Supplier Alpha")
if alpha is None:
    alpha = Supplier(organization_id=org.id, name="Supplier Alpha", city="Shanghai", country="China", categories=["components"], promised_lead_days=5, status="active")
    db.add(alpha); db.commit(); db.refresh(alpha)
beta = get_supplier("Supplier Beta")
if beta is None:
    beta = Supplier(organization_id=org.id, name="Supplier Beta", city="Taipei", country="Taiwan", categories=["components"], promised_lead_days=5, status="active")
    db.add(beta); db.commit(); db.refresh(beta)

# Seed orders if none
existing_alpha_orders = db.scalars(select(PurchaseOrder).where(PurchaseOrder.organization_id==org.id, PurchaseOrder.supplier_id==alpha.id)).all()
if not existing_alpha_orders:
    for i,(prom,act) in enumerate([(5,15),(5,10),(5,13)],start=1):
        o = PurchaseOrder(organization_id=org.id, supplier_id=alpha.id, order_number=f"A10{i}", product="component", quantity=100, order_date=datetime.now(timezone.utc)-timedelta(days=30), promised_date=datetime.now(timezone.utc)-timedelta(days=25), estimated_arrival=datetime.now(timezone.utc)-timedelta(days=25), actual_arrival=datetime.now(timezone.utc)-timedelta(days=25)+timedelta(days=act-prom), status="delivered", priority="normal", financial_impact=1000.0)
        db.add(o)
    # complaint
    db.add(SupplierComplaint(organization_id=org.id, supplier_id=alpha.id, complaint_type="quality", severity="medium", description="Defective components in batch", reported_date=datetime.now(timezone.utc)))
    db.commit()
existing_beta_orders = db.scalars(select(PurchaseOrder).where(PurchaseOrder.organization_id==org.id, PurchaseOrder.supplier_id==beta.id)).all()
if not existing_beta_orders:
    for i in range(1,4):
        o = PurchaseOrder(organization_id=org.id, supplier_id=beta.id, order_number=f"B10{i}", product="component", quantity=100, order_date=datetime.now(timezone.utc)-timedelta(days=30), promised_date=datetime.now(timezone.utc)-timedelta(days=25), estimated_arrival=datetime.now(timezone.utc)-timedelta(days=25), actual_arrival=datetime.now(timezone.utc)-timedelta(days=25), status="delivered", priority="normal", financial_impact=1000.0)
        db.add(o)
    db.commit()

# Retain verified memories
for o in db.scalars(select(PurchaseOrder).where(PurchaseOrder.organization_id==org.id, PurchaseOrder.supplier_id==alpha.id)).all():
    delay = metrics_service.delay_days(o)
    memory_service.retain(db, org, content=f"Verified: Supplier Alpha order {o.order_number} was {delay} days late (promised {o.promised_date.date()}, actual {o.actual_arrival.date()}).", category="outcome", source_type="verified_business_fact", supplier_id=alpha.id, order_id=o.id, event_date=o.actual_arrival, confidence=1.0)
for o in db.scalars(select(PurchaseOrder).where(PurchaseOrder.organization_id==org.id, PurchaseOrder.supplier_id==beta.id)).all():
    memory_service.retain(db, org, content=f"Verified: Supplier Beta order {o.order_number} delivered on time ({o.actual_arrival.date()}).", category="outcome", source_type="verified_business_fact", supplier_id=beta.id, order_id=o.id, event_date=o.actual_arrival, confidence=1.0)
memory_service.retain(db, org, content="Verified: Supplier Alpha had a quality complaint - defective components in batch.", category="episodic", source_type="verified_business_fact", supplier_id=alpha.id, confidence=1.0)

print("Seeded. Alpha metrics:", metrics_service.supplier_metrics_map(db, org.id).get(alpha.id))
print("Beta metrics:", metrics_service.supplier_metrics_map(db, org.id).get(beta.id))

# Run agent
svc = AgentService(db, org, user)
res = svc.run(message="Which supplier should we choose for an urgent order, Alpha or Beta?", new_conversation=True)
print("\n=== AGENT ANSWER ===\n", res["answer"])
print("\nMemory hits:", len(res["memory_hits"]))
print("Tool calls:", [t["name"] for t in res["tool_calls"]])
print("Model:", res["model"])
db.close()
