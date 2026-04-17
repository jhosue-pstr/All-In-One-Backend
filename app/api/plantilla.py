from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.plantilla import PlantillaCreate, PlantillaUpdate, PlantillaResponse
from app.service.plantilla import (
    create_plantilla,
    get_plantilla,
    get_plantillas,
    update_plantilla,
    delete_plantilla,
)

router = APIRouter(prefix="/plantillas", tags=["plantillas"])


@router.post("", response_model=PlantillaResponse, status_code=201)
def create(
    data: PlantillaCreate,
    db: Annotated[Session, Depends(get_db)]
):
    return create_plantilla(db, data)


@router.get("/{plantilla_id}", response_model=PlantillaResponse)
def get_one(
    plantilla_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    obj = get_plantilla(db, plantilla_id)
    if not obj:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    return obj


@router.get("", response_model=list[PlantillaResponse])
def get_all(db: Annotated[Session, Depends(get_db)]):
    return get_plantillas(db)


@router.put("/{plantilla_id}", response_model=PlantillaResponse)
def update(
    plantilla_id: int,
    data: PlantillaUpdate,
    db: Annotated[Session, Depends(get_db)]
):
    obj = update_plantilla(db, plantilla_id, data)
    if not obj:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Plantilla no encontrada")
    return obj


@router.delete("/{plantilla_id}", status_code=200)
def delete(
    plantilla_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    delete_plantilla(db, plantilla_id)
    return {"message": "Plantilla eliminada"}