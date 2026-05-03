from fastapi import Depends, HTTPException, status
from app.models.user import User, UserRole


async def require_role(allowed_roles: list[UserRole]):
    async def role_checker(current_user: User = Depends()):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this action",
            )
        return current_user

    return role_checker


async def validate_org_access(target_org_id: str, current_user: User):
    if current_user.organization_id != target_org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Different organization",
        )
