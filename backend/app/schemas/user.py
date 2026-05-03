from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole, UserStatus


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserOut(UserBase):
    id: str
    role: UserRole
    organization_id: Optional[str]
    referral_code: str
    status: UserStatus
    department: Optional[str] = None
    team: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserSearch(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: UserRole
    department: Optional[str] = None
    team: Optional[str] = None

    model_config = {"from_attributes": True}


class UserApprovalRequest(BaseModel):
    status: UserStatus
