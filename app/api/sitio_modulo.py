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


@router.get("/", response_model=list[int])
def listar_modulos(
    sitio_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    sitio = db.query(Sitio).filter(Sitio.id == sitio_id).first()
    if not sitio:
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    return [m.id for m in sitio.modulos]


@router.post("/{modulo_id}")
def agregar_modulo(
    sitio_id: int,
    modulo_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    sitio = agregar_modulo_a_sitio(db, sitio_id, modulo_id)
    if not sitio:
        raise HTTPException(status_code=404, detail="Sitio o Modulo no encontrado")
    return {"message": "Modulo agregado"}


@router.delete("/{modulo_id}")
def quitar_modulo(
    sitio_id: int,
    modulo_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    sitio = quitar_modulo_de_sitio(db, sitio_id, modulo_id)
    if not sitio:
        raise HTTPException(status_code=404, detail="Sitio o Modulo no encontrado")
    return {"message": "Modulo removido"}