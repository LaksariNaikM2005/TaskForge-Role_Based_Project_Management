import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("projects.id"), nullable=True
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id")
    )
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100))  # e.g. "created_task"
    entity_type: Mapped[str] = mapped_column(
        String(50)
    )  # "task" | "project" | "member"
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="activity_logs")
    organization = relationship("Organization")
    user = relationship("User", back_populates="activity_logs")
