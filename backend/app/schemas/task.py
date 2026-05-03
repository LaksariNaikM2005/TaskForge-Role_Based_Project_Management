from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel
from app.schemas.user import UserSearch


class TaskCreate(BaseModel):
    project_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"
    due_date: date = None
    assigned_to: Optional[str] = None
    department: str = None
    team: str = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None
    assigned_to: Optional[str] = None
    department: Optional[str] = None
    team: Optional[str] = None
    result: str


class TaskStatusUpdate(BaseModel):
    status: str


class TaskOut(BaseModel):
    id: str
    project_id: Optional[str]
    title: str
    description: Optional[str]
    status: str
    priority: str
    due_date: Optional[date]
    assigned_to: Optional[str]
    department: Optional[str]
    team: Optional[str]
    result: Optional[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
    assignee: Optional[UserSearch] = None
    creator: Optional[UserSearch] = None

    model_config = {"from_attributes": True}
