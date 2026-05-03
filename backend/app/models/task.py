import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class TaskStatus(str, enum.Enum):
    todo = "todo"
    doing = "doing"
    done = "done"


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.todo
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority), default=TaskPriority.medium
    )
    due_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Org & Hierarchy
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id")
    )
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    team: Mapped[str | None] = mapped_column(String(100), nullable=True)

    project_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("projects.id"), nullable=True
    )
    assigned_to: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
    assignee = relationship(
        "User", back_populates="assigned_tasks", foreign_keys=[assigned_to]
    )
    creator = relationship(
        "User", back_populates="created_tasks", foreign_keys=[created_by]
    )
