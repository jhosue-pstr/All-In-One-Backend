from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.plantilla import PlantillaCreate, PlantillaUpdate, PlantillaResponse
from app.service.plantilla import (
    create_plantilla,
    get_plantilla,
    get_plantillas,
    get_plantillas_publicas,
    get_plantillas_del_usuario,
    update_plantilla,
    delete_plantilla,
    es_propietario,
)
from app.api.auth import get_current_user
from app.models.usuario import User
from app.models.plantilla import Visibilidad

router = APIRouter(prefix="/plantillas", tags=["plantillas"])


@router.get("/publicas", response_model=list[PlantillaResponse])
def get_publicas(db: Annotated[Session, Depends(get_db)]):
    return get_plantillas_publicas(db)


@router.get("/mis-plantillas", response_model=list[PlantillaResponse])
def get_mis_plantillas(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    return get_plantillas_del_usuario(db, current_user.id)


@router.get("", response_model=list[PlantillaResponse])
def get_all(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)] = None
):
    if current_user:
        publicas = get_plantillas_publicas(db)
        mias = get_plantillas_del_usuario(db, current_user.id)
        return publicas + mias
    return get_plantillas_publicas(db)


@router.get("/{plantilla_id}", response_model=PlantillaResponse)
def get_one(
    plantilla_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    obj = get_plantilla(db, plantilla_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    if obj.visibilidad == Visibilidad.PRIVADA:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    return obj


@router.post("", response_model=PlantillaResponse, status_code=201)
def create(
    data: PlantillaCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    return create_plantilla(db, data, current_user.id)


@router.put("/{plantilla_id}", response_model=PlantillaResponse)
def update(
    plantilla_id: int,
    data: PlantillaUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    if not es_propietario(db, plantilla_id, current_user.id):
        raise HTTPException(status_code=403, detail="No tienes permiso para editar esta plantilla")
    obj = update_plantilla(db, plantilla_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    return obj


@router.delete("/{plantilla_id}", status_code=200)
def delete(
    plantilla_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    if not es_propietario(db, plantilla_id, current_user.id):
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta plantilla")
    delete_plantilla(db, plantilla_id)
    return {"message": "Plantilla eliminada"}