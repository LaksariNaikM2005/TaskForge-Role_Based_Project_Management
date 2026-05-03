import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.models.organization import Organization
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserOut, UserApprovalRequest
from app.services.auth_service import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if email exists
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    role = UserRole.employee
    status_val = UserStatus.pending
    org_id = None
    referred_by = None

    if data.organization_name:
        # User is creating an organization -> CEO
        org = Organization(
            name=data.organization_name, created_by="temp"
        )  # will update after user created
        db.add(org)
        await db.flush()
        org_id = org.id
        role = UserRole.ceo
        status_val = UserStatus.approved  # CEO is auto-approved
    elif data.referral_code:
        # User is joining via referral
        code = data.referral_code.strip().lower()
        ref_res = await db.execute(select(User).where(User.referral_code == code))
        referrer = ref_res.scalar_one_or_none()
        if not referrer:
            raise HTTPException(status_code=400, detail="Invalid referral code")

        org_id = referrer.organization_id
        referred_by = referrer.id

        # Determine role based on inviter
        if referrer.role == UserRole.ceo:
            role = UserRole.head
        elif referrer.role == UserRole.head:
            role = UserRole.leader
        else:
            role = UserRole.employee
    else:
        raise HTTPException(
            status_code=400, detail="Organization name or Referral code required"
        )

    user = User(
        name=data.name,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role=role,
        status=status_val,
        organization_id=org_id,
        referred_by=referred_by,
        department=data.department,
        team=data.team,
    )
    db.add(user)
    await db.flush()

    if role == UserRole.ceo:
        # Update org created_by
        org.created_by = user.id

    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user.status != UserStatus.approved:
        raise HTTPException(status_code=403, detail=f"Account status: {user.status}")

    token = create_access_token({"sub": user.id})
    return {"access_token": token, "token_type": "bearer"}


logger = logging.getLogger(__name__)


@router.post("/approve-user/{user_id}", response_model=UserOut)
async def approve_user(
    user_id: str,
    data: UserApprovalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Log the attempt
    logger.info(
        f"User {current_user.id} ({current_user.role}) attempting to {data.status} user {user_id}"
    )

    if current_user.role not in [UserRole.ceo, UserRole.head]:
        logger.warning(
            f"Unauthorized approval attempt by user {current_user.id} with role {current_user.role}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only CEO or Head of Organization can perform this action",
        )

    result = await db.execute(select(User).where(or_(User.id == user_id, User.email == user_id)))
    user = result.scalar_one_or_none()

    if not user:
        logger.error(f"Approval failed: User {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")

    if str(user.organization_id) != str(current_user.organization_id):
        logger.error(
            f"Organization mismatch: Admin {current_user.id} (Org {current_user.organization_id}) tried to approve User {user_id} (Org {user.organization_id})"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot approve users from another organization",
        )

    if user.status == data.status:
        logger.info(
            f"User {user_id} already has status {data.status}. No changes made."
        )
        return user

    user.status = data.status
    await db.commit()
    await db.refresh(user)

    logger.info(f"Successfully updated user {user_id} status to {data.status}")
    return user


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
