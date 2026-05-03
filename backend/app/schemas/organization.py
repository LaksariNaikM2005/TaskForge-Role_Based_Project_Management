from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.schemas.user import UserOut


class OrganizationCreate(BaseModel):
    name: str


class OrganizationOut(BaseModel):
    id: str
    name: str
    created_at: datetime
    created_by: str

    model_config = {"from_attributes": True}


class OrganizationDetail(OrganizationOut):
    users: List[UserOut] = []


class TeamInfo(BaseModel):
    name: str
    leader_name: Optional[str] = None
    leader_id: Optional[str] = None


class DepartmentInfo(BaseModel):
    name: str
    head_name: Optional[str] = None
    head_id: Optional[str] = None
    teams: List[TeamInfo] = []


class OrgStructure(BaseModel):
    departments: List[DepartmentInfo] = []
