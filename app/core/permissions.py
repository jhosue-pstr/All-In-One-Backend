from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.auth import get_current_user
from app.models.usuario import User
from app.models.rol import Rol, Permiso, RolPermiso


def usuario_tiene_permiso(db: Session, user: User, permiso_codigo: str) -> bool:
    if user.role == "super_admin":
        return True

    rol = db.query(Rol).filter(
        Rol.codigo == user.role,
        Rol.activo == True
    ).first()

    if not rol:
        return False

    permiso = (
        db.query(Permiso)
        .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
        .filter(
            RolPermiso.rol_id == rol.id,
            Permiso.codigo == permiso_codigo,
            Permiso.activo == True,
        )
        .first()
    )

    return permiso is not None


def require_permission(permiso_codigo: str):
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        if not usuario_tiene_permiso(db, current_user, permiso_codigo):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permiso: {permiso_codigo}",
            )
        return current_user

    return dependency