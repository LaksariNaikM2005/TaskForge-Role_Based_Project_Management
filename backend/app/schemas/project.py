from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.schemas.user import UserSearch


class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class MemberOut(BaseModel):
    id: str
    user: UserSearch
    role: str
    joined_at: datetime

    model_config = {"from_attributes": True}


class AddMemberRequest(BaseModel):
    email: str
    role: str = "member"


class ChangeMemberRoleRequest(BaseModel):
    role: str


class ProjectOut(BaseModel):
    id: str
    title: str
    description: Optional[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
    creator: UserSearch
    members: List[MemberOut] = []

    model_config = {"from_attributes": True}


class ProjectListItem(BaseModel):
    id: str
    title: str
    description: Optional[str]
    created_at: datetime
    task_count: int = 0
    member_count: int = 0
    my_role: str = "member"

    model_config = {"from_attributes": True}
