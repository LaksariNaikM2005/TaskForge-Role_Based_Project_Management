from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.schemas.organization import OrganizationOut
from app.schemas.user import UserOut
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/organization", tags=["organization"])


@router.get("/me", response_model=OrganizationOut)
async def get_my_org(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=404, detail="No organization linked")

    res = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    org = res.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.get("/members", response_model=List[UserOut])
async def get_org_members(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    res = await db.execute(
        select(User).where(User.organization_id == current_user.organization_id)
    )
    return res.scalars().all()


@router.get("/hierarchy", response_model=List[UserOut])
async def get_hierarchy(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    # CEO can see everyone. Heads can see leaders and employees. Leaders can see employees.
    query = select(User).where(User.organization_id == current_user.organization_id)

    if current_user.role == UserRole.head:
        query = query.where(User.role.in_([UserRole.leader, UserRole.employee]))
    elif current_user.role == UserRole.leader:
        query = query.where(User.role == UserRole.employee)
    elif current_user.role == UserRole.employee:
        query = query.where(User.id == current_user.id)  # Employee only sees self

    res = await db.execute(query)
    return res.scalars().all()
