from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.user import User, UserRole
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("", response_model=TaskOut, status_code=201)
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == UserRole.employee:
        raise HTTPException(status_code=403, detail="Employees cannot create tasks")

    task_data = data.model_dump()

    # Auto-fill department/team based on role if not provided
    if current_user.role == UserRole.head and not task_data.get("department"):
        task_data["department"] = current_user.department
    elif current_user.role == UserRole.leader:
        if not task_data.get("department"):
            task_data["department"] = current_user.department
        if not task_data.get("team"):
            task_data["team"] = current_user.team

    task = Task(
        **task_data,
        created_by=current_user.id,
        organization_id=current_user.organization_id
    )
    db.add(task)
    await db.commit()
    await db.refresh(task, ["creator", "assignee"])
    return task


@router.get("", response_model=List[TaskOut])
async def list_tasks(
    status: Optional[str] = Query(None),
    project_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        select(Task)
        .where(Task.organization_id == current_user.organization_id)
        .options(selectinload(Task.assignee), selectinload(Task.creator))
    )

    if status:
        query = query.where(Task.status == status)

    if project_id:
        query = query.where(Task.project_id == project_id)

    # Hierarchical filtering
    if current_user.role == UserRole.head:
        # Dept Head sees tasks for their department OR org-wide tasks
        query = query.where(
            or_(Task.department == current_user.department, Task.department.is_(None))
        )
    elif current_user.role == UserRole.leader:
        # Team Leader sees tasks for their team OR org-wide tasks
        query = query.where(
            or_(Task.team == current_user.team, Task.department.is_(None))
        )
    elif current_user.role == UserRole.employee:
        # Employees see tasks assigned to them OR their department/team
        query = query.where(
            or_(
                Task.assigned_to == current_user.id,
                and_(Task.department == current_user.department, Task.team.is_(None)),
                and_(
                    Task.department == current_user.department,
                    Task.team == current_user.team,
                ),
            )
        )
    # CEO sees everything (no additional filter)

    res = await db.execute(query)
    return res.scalars().all()


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Task)
        .where(Task.id == task_id)
        .options(selectinload(Task.assignee), selectinload(Task.creator))
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: str,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Permission check
    is_ceo = current_user.role == UserRole.ceo
    is_head_of_dept = (
        current_user.role == UserRole.head
        and task.department == current_user.department
    )
    is_leader_of_team = (
        current_user.role == UserRole.leader and task.team == current_user.team
    )
    is_assignee = task.assigned_to == current_user.id

    if not (is_ceo or is_head_of_dept or is_leader_of_team or is_assignee):
        raise HTTPException(status_code=403, detail="Not authorized to edit this task")

    update_data = data.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    task.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(task, ["creator", "assignee"])
    return task
