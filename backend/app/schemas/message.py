from datetime import datetime
from pydantic import BaseModel


class MessageBase(BaseModel):
    content: str
    receiver_id: str


class MessageCreate(MessageBase):
    pass


class MessageOut(MessageBase):
    id: str
    sender_id: str
    timestamp: datetime

    class Config:
        from_attributes = True


class ConversationSummary(BaseModel):
    user_id: str
    user_name: str
    last_message: str
    timestamp: datetime
    unread_count: int = 0
