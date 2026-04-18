from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.modulo import (
    ModuloCreate,
    ModuloUpdate,
    ModuloResponse
)
from app.service.modulo import (
    create_modulo,
    get_modulo,
    get_modulos,
    update_modulo,
    delete_modulo,
)
from app.api.auth import get_current_user
from app.models.usuario import User

router = APIRouter(prefix="/modulos", tags=["Modulos"])


@router.post("/", response_model=ModuloResponse, status_code=201)
def crear_modulo(
    data: ModuloCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    return create_modulo(db, data)


@router.get("/", response_model=list[ModuloResponse])
def listar_modulos(db: Session = Depends(get_db)):
    return get_modulos(db)


@router.get("/{modulo_id}", response_model=ModuloResponse)
def obtener_modulo(modulo_id: int, db: Session = Depends(get_db)):
    modulo = get_modulo(db, modulo_id)
    if not modulo:
        raise HTTPException(status_code=404, detail="Modulo no encontrado")
    return modulo


@router.put("/{modulo_id}", response_model=ModuloResponse)
def actualizar_modulo(
    modulo_id: int,
    data: ModuloUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    modulo = get_modulo(db, modulo_id)
    if not modulo:
        raise HTTPException(status_code=404, detail="Modulo no encontrado")

    return update_modulo(db, modulo_id, data)


@router.delete("/{modulo_id}", status_code=204)
def eliminar_modulo(
    modulo_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    modulo = get_modulo(db, modulo_id)
    if not modulo:
        raise HTTPException(status_code=404, detail="Modulo no encontrado")

    delete_modulo(db, modulo_id)