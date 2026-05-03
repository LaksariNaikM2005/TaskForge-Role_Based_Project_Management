from pydantic import BaseModel, EmailStr
from typing import Optional


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    organization_name: Optional[str] = None  # For CEO
    referral_code: Optional[str] = None  # For everyone else
    department: Optional[str] = None  # Optional for Dept Heads
    team: Optional[str] = None  # Optional for Team Leaders


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
