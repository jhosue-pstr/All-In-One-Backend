from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import uuid
from pathlib import Path
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

UPLOAD_DIR = Path("media/plantillas")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ERROR_PLANTILLA_NO_ENCONTRADA = "Plantilla no encontrada"
ERROR_SIN_PERMISO = "No tienes permiso para editar esta plantilla"
ERROR_SIN_PERMISO_ELIMINAR = "No tienes permiso para eliminar esta plantilla"


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


@router.get(
    "/{plantilla_id}",
    response_model=PlantillaResponse,
    responses={404: {"description": "Plantilla no encontrada"}}
)
def get_one(
    plantilla_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    obj = get_plantilla(db, plantilla_id)
    if not obj:
        raise HTTPException(status_code=404, detail=ERROR_PLANTILLA_NO_ENCONTRADA)
    return obj


@router.post("", response_model=PlantillaResponse, status_code=201)
def create(
    data: PlantillaCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    return create_plantilla(db, data, current_user.id)


@router.put(
    "/{plantilla_id}",
    response_model=PlantillaResponse,
    responses={
        403: {"description": "Sin permiso"},
        404: {"description": "Plantilla no encontrada"}
    }
)
def update(
    plantilla_id: int,
    data: PlantillaUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    if not es_propietario(db, plantilla_id, current_user.id):
        raise HTTPException(status_code=403, detail=ERROR_SIN_PERMISO)
    obj = update_plantilla(db, plantilla_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail=ERROR_PLANTILLA_NO_ENCONTRADA)
    return obj


@router.delete(
    "/{plantilla_id}",
    status_code=200,
    responses={403: {"description": "Sin permiso para eliminar"}}
)
def delete(
    plantilla_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    if not es_propietario(db, plantilla_id, current_user.id):
        raise HTTPException(status_code=403, detail=ERROR_SIN_PERMISO_ELIMINAR)
    delete_plantilla(db, plantilla_id)
    return {"message": "Plantilla eliminada"}


@router.post(
    "/{plantilla_id}/miniatura",
    responses={
        403: {"description": "Sin permiso"},
        404: {"description": "Plantilla no encontrada"}
    }
)
def upload_miniatura(
    plantilla_id: int,
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...)
):
    if not es_propietario(db, plantilla_id, current_user.id):
        raise HTTPException(status_code=403, detail=ERROR_SIN_PERMISO)
    
    obj = get_plantilla(db, plantilla_id)
    if not obj:
        raise HTTPException(status_code=404, detail=ERROR_PLANTILLA_NO_ENCONTRADA)
    
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    if file_ext not in ["png", "jpg", "jpeg", "webp"]:
        file_ext = "png"
    
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = UPLOAD_DIR / file_name
    
    with open(file_path, "wb") as f:
        content = file.file.read()
        f.write(content)
    
    base_url = str(request.base_url).rstrip("/")
    url = f"{base_url}/media/plantillas/{file_name}"
    
    update_plantilla(db, plantilla_id, PlantillaUpdate(miniatura=url))
    
    return {"url": url}