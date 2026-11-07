import uuid
from dataclasses import dataclass

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import get_db
from .models import AuditLog, Organization, User
from .security import decode_access_token

bearer = HTTPBearer(auto_error=False)


@dataclass
class CurrentContext:
    user: User
    organization: Organization
    request: Request | None = None


def get_current_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> CurrentContext:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = uuid.UUID(payload["sub"])
        org_id = uuid.UUID(payload["org"])
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc

    user = db.get(User, user_id)
    if user is None or not user.is_active or user.organization_id != org_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    org = db.get(Organization, org_id)
    if org is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Organization not found")
    return CurrentContext(user=user, organization=org)


def require_role(*roles: str):
    def _dep(ctx: CurrentContext = Depends(get_current_context)) -> CurrentContext:
        if roles and ctx.user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return ctx

    return _dep


def audit(
    db: Session,
    org_id: uuid.UUID,
    user_id: uuid.UUID | None,
    action: str,
    entity: str,
    entity_id: str | None = None,
    details: dict | None = None,
    ip_address: str | None = None,
) -> None:
    db.add(
        AuditLog(
            organization_id=org_id,
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            details=details or {},
            ip_address=ip_address,
        )
    )
