from fastapi import APIRouter, HTTPException, Depends, status

from app.models.user import UserRoles
from app.schemas.role_permission import RolePermission
from app.schemas.user_profile import UserProfileBase
from app.models import User, UserProfile
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.user_roles import UserRole
from app.services.user_service import get_user_by_id, service_create_user, \
    service_delete_user, service_update_user, service_create_user_profile, \
    service_assign_role, service_assign_permission

from dependencies import get_current_active_user

router = APIRouter()


@router.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int,
                    current_user: dict = Depends(get_current_active_user)):
    db_user = get_user_by_id(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db_user


@router.post("/users/", response_model=User,
             status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    return service_create_user(user)


@router.post("/users/profile", response_model=UserProfile,
             status_code=status.HTTP_201_CREATED)
async def create_user_profile(user_profile: UserProfileBase):
    return service_create_user_profile(user_profile)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int,
                      current_user: dict = Depends(get_current_active_user)):
    db_user = get_user_by_id(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_deleted = service_delete_user(user_id)
    if db_deleted is None:
        raise HTTPException(status_code=409,
                            detail="User logical constraints")
    return


@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserUpdate,
                      current_user: dict = Depends(get_current_active_user)):
    return service_update_user(user_id, user)


@router.post("/users/assign_roles", response_model=UserRoles,
             status_code=status.HTTP_201_CREATED)
async def user_assign_roles(user_roles: UserRole):
    return service_assign_role(user_roles)


@router.post("/users/assign_permission", response_model=RolePermission,
             status_code=status.HTTP_201_CREATED)
async def assign_permission(role_permission: RolePermission):
    return service_assign_permission(role_permission)
