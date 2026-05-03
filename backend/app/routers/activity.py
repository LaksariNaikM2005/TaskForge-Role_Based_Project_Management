from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.project_member import ProjectMember
from app.schemas.activity import ActivityOut
from app.services.activity_service import get_project_activity
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/activity", tags=["activity"])


@router.get("/{project_id}", response_model=List[ActivityOut])
async def get_activity(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    m_res = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
        )
    )
    if not m_res.scalar_one_or_none():
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Not a member")
    return await get_project_activity(db, project_id)
