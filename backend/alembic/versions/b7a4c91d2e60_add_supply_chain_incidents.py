"""Add tenant-scoped supply chain incidents.

Revision ID: b7a4c91d2e60
Revises: 8df7a0f2787c
"""
from __future__ import annotations
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "b7a4c91d2e60"
down_revision: Union[str, None] = "8df7a0f2787c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        "supply_chain_incidents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("incident_number", sa.String(40), nullable=False),
        sa.Column("crisis_type", sa.String(40), nullable=False),
        sa.Column("title", sa.String(250), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("supplier_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("product_component", sa.String(200), nullable=False),
        sa.Column("origin", sa.String(200), nullable=True),
        sa.Column("destination", sa.String(200), nullable=True),
        sa.Column("expected_delay_days", sa.Integer(), nullable=True),
        sa.Column("available_inventory_quantity", sa.Integer(), nullable=True),
        sa.Column("affected_orders", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("urgency", sa.String(20), nullable=False, server_default="Medium"),
        sa.Column("incident_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reported_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("synthetic", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["supplier_id"], ["suppliers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["order_id"], ["purchase_orders.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["reported_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "incident_number", name="uq_incident_org_number"),
    )
    op.create_index("ix_supply_chain_incidents_organization_id", "supply_chain_incidents", ["organization_id"])
    op.create_index("ix_supply_chain_incidents_supplier_id", "supply_chain_incidents", ["supplier_id"])
    op.create_index("ix_supply_chain_incidents_order_id", "supply_chain_incidents", ["order_id"])
    op.create_index("ix_incidents_org_status", "supply_chain_incidents", ["organization_id", "status"])
    op.create_index("ix_incidents_org_date", "supply_chain_incidents", ["organization_id", "incident_date"])

def downgrade() -> None:
    op.drop_index("ix_incidents_org_date", table_name="supply_chain_incidents")
    op.drop_index("ix_incidents_org_status", table_name="supply_chain_incidents")
    op.drop_index("ix_supply_chain_incidents_order_id", table_name="supply_chain_incidents")
    op.drop_index("ix_supply_chain_incidents_supplier_id", table_name="supply_chain_incidents")
    op.drop_index("ix_supply_chain_incidents_organization_id", table_name="supply_chain_incidents")
    op.drop_table("supply_chain_incidents")
