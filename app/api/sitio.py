from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Request,
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uuid
import anyio
from pathlib import Path

from app.db.database import get_db
from app.schemas.sitio import SitioCreate, SitioUpdate, SitioResponse
from app.service.sitio import (
    create_sitio,
    get_sitio,
    get_sitios,
    get_sitios_del_usuario,
    update_sitio,
    delete_sitio,
)
from app.core.permissions import require_permission
from app.models.usuario import User


router = APIRouter(
    prefix="/sitios",
    tags=["Gestión de Sitios"],
)

UPLOAD_DIR = Path("media/sitios")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ERROR_SITIO_NO_ENCONTRADO = "Sitio no encontrado"


def validar_existencia_sitio(db: Session, sitio_id: int):
    """
    Valida que el sitio exista.

    La autorización ya se controla antes con require_permission().
    Ejemplo:
    - sitios.ver
    - sitios.editar
    - sitios.eliminar

    Por eso aquí NO validamos propietario, porque ahora el sistema usa roles y permisos.
    """
    sitio = get_sitio(db, sitio_id)

    if not sitio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_SITIO_NO_ENCONTRADO,
        )

    return sitio


@router.post(
    "/",
    response_model=SitioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo sitio web",
)
def crear_sitio(
    data: SitioCreate,
    current_user: Annotated[User, Depends(require_permission("sitios.crear"))],
    db: Annotated[Session, Depends(get_db)],
):
    return create_sitio(db, data, current_user.id)


@router.get(
    "/",
    response_model=list[SitioResponse],
    summary="Listar todos los sitios",
)
def listar_sitios(
    current_user: Annotated[User, Depends(require_permission("sitios.ver"))],
    db: Annotated[Session, Depends(get_db)],
):
    return get_sitios(db)


@router.get(
    "/mis-sitios",
    response_model=list[SitioResponse],
    summary="Obtener mis sitios",
)
def mis_sitios(
    current_user: Annotated[User, Depends(require_permission("sitios.ver"))],
    db: Annotated[Session, Depends(get_db)],
):
    return get_sitios_del_usuario(db, current_user.id)


@router.get(
    "/{sitio_id}",
    response_model=SitioResponse,
    summary="Obtener sitio por ID",
)
def obtener_sitio(
    sitio_id: int,
    current_user: Annotated[User, Depends(require_permission("sitios.ver"))],
    db: Annotated[Session, Depends(get_db)],
):
    return validar_existencia_sitio(db, sitio_id)


@router.put(
    "/{sitio_id}",
    response_model=SitioResponse,
    summary="Actualizar sitio web",
)
def actualizar_sitio(
    sitio_id: int,
    data: SitioUpdate,
    current_user: Annotated[User, Depends(require_permission("sitios.editar"))],
    db: Annotated[Session, Depends(get_db)],
):
    validar_existencia_sitio(db, sitio_id)

    return update_sitio(
        db,
        sitio_id,
        data,
        current_user.id,
    )


@router.delete(
    "/{sitio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar sitio web",
)
def eliminar_sitio(
    sitio_id: int,
    current_user: Annotated[User, Depends(require_permission("sitios.eliminar"))],
    db: Annotated[Session, Depends(get_db)],
):
    validar_existencia_sitio(db, sitio_id)

    delete_sitio(
        db,
        sitio_id,
        current_user.id,
    )

    return None


@router.post(
    "/{sitio_id}/miniatura",
    summary="Subir miniatura del sitio",
)
async def upload_miniatura(
    sitio_id: int,
    request: Request,
    current_user: Annotated[User, Depends(require_permission("sitios.editar"))],
    db: Annotated[Session, Depends(get_db)],
    file: Annotated[UploadFile, File(...)],
):
    """
    Subir miniatura cuenta como editar sitio.

    Por eso usa:
    - require_permission("sitios.editar")

    Ya no se bloquea por propietario, porque editor_sitios debe poder editar sitios.
    """
    validar_existencia_sitio(db, sitio_id)

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo no tiene nombre válido",
        )

    file_ext = (
        file.filename.split(".")[-1].lower()
        if "." in file.filename
        else "png"
    )

    if file_ext not in ["png", "jpg", "jpeg", "webp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato no permitido. Usa PNG, JPG, JPEG o WEBP",
        )

    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = UPLOAD_DIR / file_name

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo está vacío",
        )

    await anyio.Path(file_path).write_bytes(content)

    base_url = str(request.base_url).rstrip("/")
    url = f"{base_url}/media/sitios/{file_name}"

    update_sitio(
        db,
        sitio_id,
        SitioUpdate(miniatura=url),
        current_user.id,
    )

    return JSONResponse(
        status_code=200,
        content={
            "message": "Miniatura subida correctamente",
            "url": url,
        },
    )