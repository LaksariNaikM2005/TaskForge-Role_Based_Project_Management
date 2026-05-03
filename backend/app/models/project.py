import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    creator = relationship(
        "User", back_populates="created_projects", foreign_keys=[created_by]
    )
    members = relationship(
        "ProjectMember", back_populates="project", cascade="all, delete-orphan"
    )
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    activity_logs = relationship(
        "ActivityLog", back_populates="project", cascade="all, delete-orphan"
    )
