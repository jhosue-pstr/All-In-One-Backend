from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.service.sitio_modulo import (
    agregar_modulo_a_sitio,
    quitar_modulo_de_sitio,
    get_modulos_del_sitio
)
from app.models.sitio import Sitio
from app.models.modulo import Modulo
from app.api.auth import get_current_user
from app.models.usuario import User

router = APIRouter(prefix="/sitios/{sitio_id}/modulos", tags=["Sitio-Modulos"])

ERROR_SITIO_NO_ENCONTRADO = "Sitio no encontrado"
ERROR_SITIO_O_MODULO_NO_ENCONTRADO = "Sitio o Modulo no encontrado"
ERROR_SIN_PERMISO = "No tienes permiso para modificar los módulos de este sitio"

# Helper de seguridad para verificar propiedad
def es_propietario_sitio(db: Session, sitio_id: int, usuario_id: int):
    sitio = db.query(Sitio).filter(Sitio.id == sitio_id).first()
    if not sitio:
        return False
    return sitio.id_usuario == usuario_id


@router.get(
    "/",
    response_model=list[int],
    responses={404: {"description": "Sitio no encontrado"}}
)
def listar_modulos(
    sitio_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    sitio = db.query(Sitio).filter(Sitio.id == sitio_id).first()
    if not sitio:
        raise HTTPException(status_code=404, detail=ERROR_SITIO_NO_ENCONTRADO)
    return [m.id for m in sitio.modulos]


@router.post(
    "/{modulo_id}",
    responses={
        404: {"description": "Sitio o Modulo no encontrado"},
        403: {"description": "Sin permiso"}
    }
)
def agregar_modulo(
    sitio_id: int,
    modulo_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    # Validar propiedad antes de agregar
    if not es_propietario_sitio(db, sitio_id, current_user.id):
        raise HTTPException(status_code=403, detail=ERROR_SIN_PERMISO)

    # Pasar current_user.id para la auditoría
    sitio = agregar_modulo_a_sitio(db, sitio_id, modulo_id, current_user.id)
    if not sitio:
        raise HTTPException(status_code=404, detail=ERROR_SITIO_O_MODULO_NO_ENCONTRADO)
    return {"message": "Modulo agregado"}


@router.delete(
    "/{modulo_id}",
    responses={
        404: {"description": "Sitio o Modulo no encontrado"},
        403: {"description": "Sin permiso"}
    }
)
def quitar_modulo(
    sitio_id: int,
    modulo_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    # Validar propiedad antes de quitar
    if not es_propietario_sitio(db, sitio_id, current_user.id):
        raise HTTPException(status_code=403, detail=ERROR_SIN_PERMISO)

    # Pasar current_user.id para la auditoría
    sitio = quitar_modulo_de_sitio(db, sitio_id, modulo_id, current_user.id)
    if not sitio:
        raise HTTPException(status_code=404, detail=ERROR_SITIO_O_MODULO_NO_ENCONTRADO)
    return {"message": "Modulo removido"}