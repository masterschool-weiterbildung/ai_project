from fastapi import APIRouter, HTTPException, Depends, status

from app.models.user import Roles
from app.schemas.roles import RoleBase
from app.services.roles_service import service_get_role_by_id, \
    service_get_role_by_name, service_create_role, service_delete_role, \
    service_update_role
from dependencies import get_current_active_user

router = APIRouter()


@router.get("/roles/{role_id}", response_model=Roles)
async def read_user_by_Id(role_id: int,
                          current_user: dict = Depends(
                              get_current_active_user)):
    db_role = service_get_role_by_id(role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")

    return db_role


@router.get("/roles/{role_name}", response_model=Roles)
async def read_user_by_Name(role_name: str,
                            current_user: dict = Depends(
                                get_current_active_user)):
    db_role = service_get_role_by_name(role_name)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")

    return db_role


@router.post("/roles/", response_model=Roles,
             status_code=status.HTTP_201_CREATED)
async def create_role(role: RoleBase):
    db_role = service_create_role(role)
    return db_role


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: int,
                      current_user: dict = Depends(get_current_active_user)):
    db_role = read_user_by_Id(role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    db_deleted = service_delete_role(role_id)
    if db_deleted is None:
        raise HTTPException(status_code=409,
                            detail="Role logical constraints")
    return


@router.put("/roles/{role_id}", response_model=Roles)
async def update_user(role_id: int, role: RoleBase,
                      current_user: dict = Depends(get_current_active_user)):
    return service_update_role(role_id, role)
