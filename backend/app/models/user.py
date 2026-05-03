import uuid
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class UserRole(str, enum.Enum):
    ceo = "ceo"
    head = "head"
    leader = "leader"
    employee = "employee"


class UserStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)

    # Hierarchy & Org
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.employee)
    organization_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("organizations.id")
    )
    referred_by: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id")
    )
    referral_code: Mapped[str] = mapped_column(
        String(36), unique=True, default=lambda: str(uuid.uuid4())[:8]
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus), default=UserStatus.pending
    )
    department: Mapped[Optional[str]] = mapped_column(String(100))
    team: Mapped[Optional[str]] = mapped_column(String(100))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    # Project memberships (keeping for backward compatibility or department use)
    project_memberships = relationship(
        "ProjectMember", back_populates="user", cascade="all, delete-orphan"
    )
    created_projects = relationship(
        "Project", back_populates="creator", foreign_keys="Project.created_by"
    )

    assigned_tasks = relationship(
        "Task", back_populates="assignee", foreign_keys="Task.assigned_to"
    )
    created_tasks = relationship(
        "Task", back_populates="creator", foreign_keys="Task.created_by"
    )

    activity_logs = relationship("ActivityLog", back_populates="user")

    # Hierarchy relationships
    referrals = relationship("User", back_populates="inviter")
    inviter = relationship("User", back_populates="referrals", remote_side=[id])
