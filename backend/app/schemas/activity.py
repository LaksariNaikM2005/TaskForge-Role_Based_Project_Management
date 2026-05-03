from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.user import UserSearch


class ActivityOut(BaseModel):
    id: str
    project_id: str
    action: str
    entity_type: str
    entity_id: Optional[str]
    details: Optional[str]
    created_at: datetime
    user: UserSearch

    model_config = {"from_attributes": True}
