from fastapi import APIRouter, HTTPException, Depends, status

from app.models.user import Roles, Permissions
from app.schemas.permissions import PermissionBase
from app.services.permissions_service import service_get_permission_by_id, \
    service_get_permission_by_name, service_create_permission, \
    service_delete_permission, service_update_permission

from dependencies import get_current_active_user

router = APIRouter()


@router.get("/permissions/{permission_id}", response_model=Permissions)
async def read_permission_by_Id(permission_id: int,
                                current_user: dict = Depends(
                                    get_current_active_user)):
    db_permission = service_get_permission_by_id(permission_id)
    if db_permission is None:
        raise HTTPException(status_code=404, detail="Permission not found")

    return db_permission


@router.get("/permissions/{permission_name}", response_model=Permissions)
async def read_permission_by_Name(permission_name: str,
                                  current_user: dict = Depends(
                                      get_current_active_user)):
    db_permission = service_get_permission_by_name(permission_name)
    if db_permission is None:
        raise HTTPException(status_code=404, detail="Permission not found")

    return db_permission


@router.post("/permissions/", response_model=Permissions,
             status_code=status.HTTP_201_CREATED)
async def create_permission(permission: PermissionBase):
    db_permission = service_create_permission(permission)
    return db_permission


@router.delete("/permissions/{permission_id}",
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(permission_id: int,
                            current_user: dict = Depends(
                                get_current_active_user)):
    db_permission = read_permission_by_Id(permission_id)
    if db_permission is None:
        raise HTTPException(status_code=404, detail="Permission not found")
    db_permission = service_delete_permission(permission_id)
    if db_permission is None:
        raise HTTPException(status_code=409,
                            detail="Permission logical constraints")
    return


@router.put("/permissions/{permission_id}", response_model=Permissions)
async def update_permission(permission_id: int, permission: PermissionBase,
                            current_user: dict = Depends(
                                get_current_active_user)):
    return service_update_permission(permission_id, permission)
