from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, desc
from app.database import get_db
from app.models.user import User
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageOut, ConversationSummary
from app.dependencies.auth import get_current_user
from typing import List

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.post("/", response_model=MessageOut)
async def send_message(
    data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify receiver exists and is in the same org
    res = await db.execute(select(User).where(User.id == data.receiver_id))
    receiver = res.scalar_one_or_none()

    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    if receiver.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=403, detail="Cannot message users outside your organization"
        )

    message = Message(
        sender_id=current_user.id, receiver_id=data.receiver_id, content=data.content
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


@router.get("/recent", response_model=List[ConversationSummary])
async def get_recent_conversations(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    # This is a bit complex for a simple SQL query in async mode without group_by issues
    # Let's just get all users in the org for now as potential "contacts"
    res = await db.execute(
        select(User).where(
            and_(
                User.organization_id == current_user.organization_id,
                User.id != current_user.id,
            )
        )
    )
    users = res.scalars().all()

    summaries = []
    for user in users:
        # Get last message
        msg_res = await db.execute(
            select(Message)
            .where(
                or_(
                    and_(
                        Message.sender_id == current_user.id,
                        Message.receiver_id == user.id,
                    ),
                    and_(
                        Message.sender_id == user.id,
                        Message.receiver_id == current_user.id,
                    ),
                )
            )
            .order_by(desc(Message.timestamp))
            .limit(1)
        )
        last_msg = msg_res.scalar_one_or_none()

        summaries.append(
            {
                "user_id": user.id,
                "user_name": user.name,
                "last_message": last_msg.content if last_msg else "No messages yet",
                "timestamp": last_msg.timestamp if last_msg else user.created_at,
                "unread_count": 0,  # Placeholder
            }
        )

    # Sort by timestamp
    summaries.sort(key=lambda x: x["timestamp"], reverse=True)
    return summaries


@router.get("/{user_id}", response_model=List[MessageOut])
async def get_conversation(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    res = await db.execute(
        select(Message)
        .where(
            or_(
                and_(
                    Message.sender_id == current_user.id, Message.receiver_id == user_id
                ),
                and_(
                    Message.sender_id == user_id, Message.receiver_id == current_user.id
                ),
            )
        )
        .order_by(Message.timestamp)
    )
    return res.scalars().all()
