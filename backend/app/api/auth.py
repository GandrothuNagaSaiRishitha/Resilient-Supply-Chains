"""Authentication and organization bootstrap."""

from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..db import get_db
from ..deps import CurrentContext, audit, get_current_context
from ..models import Membership, Organization, User
from ..schemas import AuthResponse, LoginRequest, MeResponse, OrganizationOut, RegisterRequest, UserOut
from ..security import create_access_token, hash_password, verify_password
from ..services import memory as memory_service
from ..services.seed import DEMO_EMAIL, DEMO_PASSWORD, demo_exists, seed_demo

logger = logging.getLogger("supplymind.auth")
router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:100] or "organization"


def _auth_response(user: User, organization: Organization) -> AuthResponse:
    token = create_access_token(str(user.id), str(organization.id), {"email": user.email, "role": user.role})
    return AuthResponse(
        access_token=token,
        user=UserOut.model_validate(user),
        organization=OrganizationOut.model_validate(organization),
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)) -> AuthResponse:
    email = payload.email.lower().strip()
    if db.scalar(select(User).where(func.lower(User.email) == email)):
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    base_slug = _slugify(payload.organization_name)
    slug = base_slug
    suffix = 1
    while db.scalar(select(Organization).where(Organization.slug == slug)):
        suffix += 1
        slug = f"{base_slug}-{suffix}"[:110]

    # Bank ids are always generated on the server; clients never supply them.
    bank_id = f"sm_{uuid.uuid4().hex[:16]}"
    organization = Organization(
        name=payload.organization_name.strip(),
        slug=slug,
        memory_bank_id=bank_id,
        is_demo=False,
    )
    db.add(organization)
    db.commit()
    db.refresh(organization)

    user = User(
        organization_id=organization.id,
        email=email,
        full_name=payload.full_name.strip(),
        password_hash=hash_password(payload.password),
        role="owner",
        is_active=True,
        last_login_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.add(Membership(organization_id=organization.id, user_id=user.id, role="owner"))
    audit(
        db,
        organization.id,
        user.id,
        "auth.register",
        "organization",
        str(organization.id),
        {"slug": slug},
        request.client.host if request.client else None,
    )
    db.commit()

    try:
        memory_service.ensure_bank(organization)
    except Exception as exc:  # noqa: BLE001
        logger.warning("could not create Hindsight bank at registration: %s", exc)

    return _auth_response(user, organization)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> AuthResponse:
    email = payload.email.lower().strip()
    user = db.scalar(select(User).where(func.lower(User.email) == email))
    if user is None or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    organization = db.get(Organization, user.organization_id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Organization not found")
    user.last_login_at = datetime.now(timezone.utc)
    audit(
        db,
        organization.id,
        user.id,
        "auth.login",
        "user",
        str(user.id),
        {},
        request.client.host if request.client else None,
    )
    db.commit()
    return _auth_response(user, organization)


@router.post("/demo-login", response_model=AuthResponse)
def demo_login(request: Request, db: Session = Depends(get_db)) -> AuthResponse:
    """Log into the labeled synthetic demo organization, seeding it once if needed."""
    if not demo_exists(db):
        logger.info("demo organization missing; seeding synthetic dataset and Hindsight memories")
        seed_demo(db, force=False, retain_memories=True)
    user = db.scalar(select(User).where(func.lower(User.email) == DEMO_EMAIL))
    if user is None:
        raise HTTPException(status_code=500, detail="Demo user could not be created")
    organization = db.get(Organization, user.organization_id)
    if organization is None:
        raise HTTPException(status_code=500, detail="Demo organization could not be created")
    user.last_login_at = datetime.now(timezone.utc)
    audit(
        db,
        organization.id,
        user.id,
        "auth.demo_login",
        "user",
        str(user.id),
        {"synthetic_demo": True},
        request.client.host if request.client else None,
    )
    db.commit()
    return _auth_response(user, organization)


@router.get("/me", response_model=MeResponse)
def me(ctx: CurrentContext = Depends(get_current_context)) -> MeResponse:
    return MeResponse(
        user=UserOut.model_validate(ctx.user),
        organization=OrganizationOut.model_validate(ctx.organization),
    )
