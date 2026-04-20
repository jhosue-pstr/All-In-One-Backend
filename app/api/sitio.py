from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uuid
from pathlib import Path
from app.db.database import get_db
from app.schemas.sitio import SitioCreate, SitioUpdate, SitioResponse
from app.service.sitio import (
    create_sitio,
    get_sitio,
    get_sitios,
    get_sitios_del_usuario,
    update_sitio,
    delete_sitio
)
from app.api.auth import get_current_user
from app.models.usuario import User

router = APIRouter(prefix="/sitios", tags=["Sitios"])

UPLOAD_DIR = Path("media/sitios")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/", response_model=SitioResponse, status_code=201)
def crear_sitio(
    data: SitioCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    return create_sitio(db, data, current_user.id)


@router.get("/", response_model=list[SitioResponse])
def listar_sitios(db: Session = Depends(get_db)):
    return get_sitios(db)


@router.get("/mis-sitios", response_model=list[SitioResponse])
def mis_sitios(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    return get_sitios_del_usuario(db, current_user.id)


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


def es_propietario(db: Session, sitio_id: int, usuario_id: int):
    sitio = get_sitio(db, sitio_id)
    if not sitio:
        return False
    return sitio.id_usuario == usuario_id


@router.post("/{sitio_id}/miniatura")
def upload_miniatura(
    sitio_id: int,
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    file: UploadFile = File(...)
):
    if not es_propietario(db, sitio_id, current_user.id):
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este sitio")
    
    obj = get_sitio(db, sitio_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Sitio no encontrado")
    
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "png"
    if file_ext not in ["png", "jpg", "jpeg", "webp"]:
        file_ext = "png"
    
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = UPLOAD_DIR / file_name
    
    with open(file_path, "wb") as f:
        content = file.file.read()
        f.write(content)
    
    base_url = str(request.base_url).rstrip("/")
    url = f"{base_url}/media/sitios/{file_name}"
    
    update_sitio(db, sitio_id, SitioUpdate(miniatura=url))
    
    return {"url": url}