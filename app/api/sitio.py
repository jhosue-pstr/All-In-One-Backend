from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.sitio import SitioCreate, SitioUpdate, SitioResponse
from app.service.sitio import (
    create_sitio,
    get_sitio,
    get_sitios,
    update_sitio,
    delete_sitio
)
from app.api.auth import get_current_user
from app.models.usuario import User

router = APIRouter(prefix="/sitios", tags=["Sitios"])


@router.post("/", response_model=SitioResponse, status_code=201)
def crear_sitio(
    data: SitioCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    return create_sitio(db, data)


@router.get("/", response_model=list[SitioResponse])
def listar_sitios(db: Session = Depends(get_db)):
    return get_sitios(db)


@router.get("/{sitio_id}", response_model=SitioResponse)
def obtener_sitio(sitio_id: int, db: Session = Depends(get_db)):
    sitio = get_sitio(db, sitio_id)
    if not sitio:
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    return sitio


@router.put("/{sitio_id}", response_model=SitioResponse)
def actualizar_sitio(
    sitio_id: int,
    data: SitioUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    sitio = get_sitio(db, sitio_id)
    if not sitio:
        raise HTTPException(status_code=404, detail="Sitio no encontrado")

    return update_sitio(db, sitio_id, data)


@router.delete("/{sitio_id}", status_code=204)
def eliminar_sitio(
    sitio_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    sitio = get_sitio(db, sitio_id)
    if not sitio:
        raise HTTPException(status_code=404, detail="Sitio no encontrado")

    delete_sitio(db, sitio_id)