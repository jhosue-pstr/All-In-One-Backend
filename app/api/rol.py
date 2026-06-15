from typing import Annotated
from fastapi import APIRouter, Depends, Body, status
from sqlalchemy.orm import Session
from app.api.auth import get_current_user
from app.db.database import get_db
from app.models.usuario import User
from app.core.permissions import require_permission
from app.service.rol import RolService
from app.schemas.rol import (
    RolCreate,
    RolUpdate,
    RolResponse,
    PermisoResponse,
    UsuarioSistemaCreate,
    UsuarioSistemaResponse,
    CambiarRolUsuario,
)


router = APIRouter(prefix="/roles", tags=["Roles y Permisos"])


def formatear_rol(rol):
    return {
        "id": rol.id,
        "nombre": rol.nombre,
        "codigo": rol.codigo,
        "descripcion": rol.descripcion,
        "activo": rol.activo,
        "es_sistema": rol.es_sistema,
        "permisos": [
            rp.permiso.codigo
            for rp in rol.permisos
            if rp.permiso is not None and rp.permiso.activo
        ],
    }

@router.get("/mis-permisos")
def obtener_mis_permisos(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    service = RolService(db)

    return {
        "usuario_id": current_user.id,
        "correo": current_user.correo,
        "role": current_user.role,
        "permisos": service.obtener_permisos_usuario(current_user),
    }
@router.get("/permisos", response_model=list[PermisoResponse])
def listar_permisos(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("roles.ver"))],
):
    service = RolService(db)
    return service.listar_permisos()


@router.get("", response_model=list[RolResponse])
def listar_roles(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("roles.ver"))],
):
    service = RolService(db)
    roles = service.listar_roles()
    return [formatear_rol(rol) for rol in roles]


@router.post("", response_model=RolResponse, status_code=status.HTTP_201_CREATED)
def crear_rol(
    data: Annotated[RolCreate, Body()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("roles.crear"))],
):
    service = RolService(db)
    rol = service.crear_rol(data, usuario_id=current_user.id)
    return formatear_rol(rol)


@router.put("/{rol_id}", response_model=RolResponse)
def actualizar_rol(
    rol_id: int,
    data: Annotated[RolUpdate, Body()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("roles.editar"))],
):
    service = RolService(db)
    rol = service.actualizar_rol(rol_id, data, usuario_id=current_user.id)
    return formatear_rol(rol)


@router.delete("/{rol_id}")
def eliminar_rol(
    rol_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("roles.eliminar"))],
):
    service = RolService(db)
    return service.eliminar_rol(rol_id, usuario_id=current_user.id)


@router.get("/usuarios", response_model=list[UsuarioSistemaResponse])
def listar_usuarios(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("roles.usuarios"))],
):
    service = RolService(db)
    return service.listar_usuarios()


@router.post("/usuarios", response_model=UsuarioSistemaResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario_sistema(
    data: Annotated[UsuarioSistemaCreate, Body()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("roles.usuarios"))],
):
    service = RolService(db)
    return service.crear_usuario_sistema(data, usuario_id=current_user.id)


@router.put("/usuarios/{user_id}/rol", response_model=UsuarioSistemaResponse)
def cambiar_rol_usuario(
    user_id: int,
    data: Annotated[CambiarRolUsuario, Body()],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("roles.usuarios"))],
):
    service = RolService(db)
    return service.cambiar_rol_usuario(user_id, data.role, usuario_id=current_user.id)


@router.delete("/usuarios/{user_id}")
def desactivar_usuario(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("roles.usuarios"))],
):
    service = RolService(db)
    return service.desactivar_usuario(user_id, usuario_id=current_user.id)

@router.put("/usuarios/{user_id}/activar", response_model=UsuarioSistemaResponse)
def activar_usuario(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("roles.usuarios"))],
):
    service = RolService(db)
    return service.activar_usuario(user_id, usuario_id=current_user.id)