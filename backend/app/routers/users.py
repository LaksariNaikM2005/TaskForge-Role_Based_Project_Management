from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserSearch
from app.schemas.organization import OrgStructure, DepartmentInfo, TeamInfo
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/org-structure", response_model=OrgStructure)
async def get_org_structure(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the full organizational structure (departments/teams)."""
    # Fetch all users in the organization to build the hierarchy
    res = await db.execute(
        select(User).where(User.organization_id == current_user.organization_id)
    )
    users = res.scalars().all()

    # Organize data
    departments_dict = {}

    # First pass: Identify departments and their heads
    for user in users:
        if not user.department:
            continue

        if user.department not in departments_dict:
            departments_dict[user.department] = {
                "name": user.department,
                "head_name": "No Head",
                "head_id": None,
                "teams": {},
            }

        if user.role == UserRole.head:
            departments_dict[user.department]["head_name"] = user.name
            departments_dict[user.department]["head_id"] = user.id

    # Second pass: Identify teams and their leaders
    for user in users:
        if not user.department or not user.team:
            continue

        dept_info = departments_dict.get(user.department)
        if not dept_info:
            continue  # Should not happen based on first pass

        if user.team not in dept_info["teams"]:
            dept_info["teams"][user.team] = {
                "name": user.team,
                "leader_name": "No Leader",
                "leader_id": None,
            }

        if user.role == UserRole.leader:
            dept_info["teams"][user.team]["leader_name"] = user.name
            dept_info["teams"][user.team]["leader_id"] = user.id

    # Build final structure
    structure = OrgStructure()
    for dept_name, dept_data in departments_dict.items():
        teams = [TeamInfo(**t) for t in dept_data["teams"].values()]
        dept_info = DepartmentInfo(
            name=dept_data["name"],
            head_name=dept_data["head_name"],
            head_id=dept_data["head_id"],
            teams=teams,
        )
        structure.departments.append(dept_info)

    return structure


@router.get("", response_model=List[UserSearch])
async def search_users(
    q: str = Query(default="", min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.email.contains(q)).limit(10))
    return result.scalars().all()
