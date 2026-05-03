import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.database import Base


class MemberRole(str, enum.Enum):
    admin = "admin"
    member = "member"


class ProjectMember(Base):
    __tablename__ = "project_members"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    role: Mapped[str] = mapped_column(
        SAEnum(MemberRole, native_enum=False), default=MemberRole.member
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")
