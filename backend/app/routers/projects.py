from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.project_member import ProjectMember, MemberRole
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectOut,
    ProjectListItem,
    AddMemberRequest,
)
from app.dependencies.auth import get_current_user
from app.services.activity_service import log_activity
from app.routers.ws import manager

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectOut, status_code=201)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = Project(**data.model_dump(), created_by=current_user.id)
    db.add(project)
    await db.flush()
    # Creator becomes admin
    membership = ProjectMember(
        project_id=project.id, user_id=current_user.id, role=MemberRole.admin
    )
    db.add(membership)
    await log_activity(
        db, project.id, current_user.id, current_user.organization_id, "created_project", "project", project.id
    )
    await db.commit()
    await db.refresh(project, ["creator", "members"])
    return project


@router.get("", response_model=List[ProjectListItem])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ProjectMember).where(ProjectMember.user_id == current_user.id)
    )
    memberships = result.scalars().all()
    items = []
    for m in memberships:
        p_res = await db.execute(select(Project).where(Project.id == m.project_id))
        project = p_res.scalar_one_or_none()
        if not project:
            continue
        members_res = await db.execute(
            select(ProjectMember).where(ProjectMember.project_id == project.id)
        )
        member_count = len(members_res.scalars().all())
        items.append(
            ProjectListItem(
                id=project.id,
                title=project.title,
                description=project.description,
                created_at=project.created_at,
                member_count=member_count,
                my_role=m.role,
            )
        )
    return items


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify membership
    m_res = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
        )
    )
    if not m_res.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not a member of this project")
    p_res = await db.execute(select(Project).where(Project.id == project_id))
    project = p_res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.refresh(project, ["creator", "members"])
    for member in project.members:
        await db.refresh(member, ["user"])
    return project


@router.put("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    m_res = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
        )
    )
    membership = m_res.scalar_one_or_none()
    if not membership or membership.role != MemberRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    p_res = await db.execute(select(Project).where(Project.id == project_id))
    project = p_res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(project, field, value)
    project.updated_at = datetime.utcnow()
    await log_activity(
        db, project_id, current_user.id, current_user.organization_id, "updated_project", "project", project_id
    )
    await db.commit()
    await db.refresh(project, ["creator", "members"])
    await manager.broadcast(
        project_id, {"type": "project_updated", "project_id": project_id}
    )
    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(
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
    membership = m_res.scalar_one_or_none()
    if not membership or membership.role != MemberRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    p_res = await db.execute(select(Project).where(Project.id == project_id))
    project = p_res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)
    await db.commit()


@router.post("/{project_id}/members", status_code=201)
async def add_member(
    project_id: str,
    data: AddMemberRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    m_res = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
        )
    )
    membership = m_res.scalar_one_or_none()
    if not membership or membership.role != MemberRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    u_res = await db.execute(select(User).where(User.email == data.email))
    user = u_res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    existing = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user.id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User already a member")
    new_member = ProjectMember(project_id=project_id, user_id=user.id, role=data.role)
    db.add(new_member)
    await log_activity(
        db,
        project_id,
        current_user.id,
        current_user.organization_id,
        "added_member",
        "member",
        user.id,
        {"email": data.email},
    )
    await db.commit()
    await manager.broadcast(
        project_id,
        {"type": "member_added", "project_id": project_id, "user_id": user.id},
    )
    return {"message": "Member added"}


@router.delete("/{project_id}/members/{user_id}", status_code=204)
async def remove_member(
    project_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    m_res = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
        )
    )
    membership = m_res.scalar_one_or_none()
    if not membership or membership.role != MemberRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    target_res = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
        )
    )
    target = target_res.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Member not found")
    await db.delete(target)
    await log_activity(
        db, project_id, current_user.id, current_user.organization_id, "removed_member", "member", user_id
    )
    await db.commit()
    await manager.broadcast(
        project_id,
        {"type": "member_removed", "project_id": project_id, "user_id": user_id},
    )
