import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.activity_log import ActivityLog


async def log_activity(
    db: AsyncSession,
    project_id: str,
    user_id: str,
    organization_id: str,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    details: dict | None = None,
) -> ActivityLog:
    log = ActivityLog(
        project_id=project_id,
        user_id=user_id,
        organization_id=organization_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=json.dumps(details) if details else None,
        created_at=datetime.utcnow(),
    )
    db.add(log)
    await db.flush()
    return log


async def get_project_activity(db: AsyncSession, project_id: str, limit: int = 50):
    # Use selectinload to eagerly fetch the user relationship in one go
    result = await db.execute(
        select(ActivityLog)
        .where(ActivityLog.project_id == project_id)
        .options(selectinload(ActivityLog.user))
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()
