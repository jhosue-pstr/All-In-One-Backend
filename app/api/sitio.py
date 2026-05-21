from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Request,
    status
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
    delete_sitio
)
from app.api.auth import get_current_user
from app.models.usuario import User

router = APIRouter(
    prefix="/sitios",
    tags=["Gestión de Sitios"]
)

UPLOAD_DIR = Path("media/sitios")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ERROR_SITIO_NO_ENCONTRADO = "Sitio no encontrado"
ERROR_SIN_PERMISO = "No tienes permiso para editar este sitio"


def es_propietario(db: Session, sitio_id: int, usuario_id: int):
    """
    Verifica si el usuario autenticado es propietario del sitio.
    """
    sitio = get_sitio(db, sitio_id)

    if not sitio:
        return False

    return sitio.id_usuario == usuario_id


@router.post(
    "/",
    response_model=SitioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo sitio web",
    description="""
## Crear sitio web

Permite crear un nuevo sitio asociado al usuario autenticado.

### Funcionalidades
- Asocia automáticamente el sitio al usuario actual
- Genera un registro persistente en base de datos
- Compatible con el sistema drag & drop

### Seguridad
Requiere autenticación JWT.

### Resultado
Retorna la información completa del sitio creado.
""",
    responses={
        201: {
            "description": "Sitio creado correctamente"
        },
        401: {
            "description": "No autenticado"
        }
    }
)
def crear_sitio(
    data: SitioCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    return create_sitio(db, data, current_user.id)


@router.get(
    "/",
    response_model=list[SitioResponse],
    summary="Listar todos los sitios",
    description="""
## Listado global de sitios

Obtiene todos los sitios registrados en el sistema.

### Información retornada
- Datos básicos del sitio
- URLs
- Miniaturas
- Estado actual

### Uso común
- Panel administrativo
- Dashboard global
- Explorador de sitios
""",
    responses={
        200: {
            "description": "Lista de sitios obtenida correctamente"
        }
    }
)
def listar_sitios(
    db: Annotated[Session, Depends(get_db)]
):
    return get_sitios(db)


@router.get(
    "/mis-sitios",
    response_model=list[SitioResponse],
    summary="Obtener mis sitios",
    description="""
## Sitios del usuario autenticado

Retorna únicamente los sitios pertenecientes al usuario autenticado.

### Seguridad
Requiere Bearer Token JWT válido.

### Resultado
Lista personalizada de sitios creados por el usuario.
""",
    responses={
        200: {
            "description": "Sitios obtenidos correctamente"
        },
        401: {
            "description": "Token inválido o expirado"
        }
    }
)
def mis_sitios(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    return get_sitios_del_usuario(db, current_user.id)


@router.get(
    "/{sitio_id}",
    response_model=SitioResponse,
    summary="Obtener sitio por ID",
    description="""
## Buscar sitio específico

Obtiene la información detallada de un sitio utilizando su ID.

### Parámetros
- sitio_id: identificador único del sitio

### Resultado
Información completa del sitio solicitado.
""",
    responses={
        200: {
            "description": "Sitio encontrado correctamente"
        },
        404: {
            "description": "Sitio no encontrado"
        }
    }
)
def obtener_sitio(
    sitio_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    sitio = get_sitio(db, sitio_id)

    if not sitio:
        raise HTTPException(
            status_code=404,
            detail=ERROR_SITIO_NO_ENCONTRADO
        )

    return sitio


@router.put(
    "/{sitio_id}",
    response_model=SitioResponse,
    summary="Actualizar sitio web",
    description="""
## Modificación de sitio

Permite actualizar la información de un sitio existente.

### Seguridad
Solo el propietario del sitio puede editarlo.

### Campos editables
- Nombre
- Descripción
- Configuración
- Miniatura
- Contenido visual

### Validaciones
- Verificación de existencia
- Validación de permisos
""",
    responses={
        200: {
            "description": "Sitio actualizado correctamente"
        },
        403: {
            "description": "No tienes permisos para editar este sitio"
        },
        404: {
            "description": "Sitio no encontrado"
        }
    }
)
def actualizar_sitio(
    sitio_id: int,
    data: SitioUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    sitio = get_sitio(db, sitio_id)

    if not sitio:
        raise HTTPException(
            status_code=404,
            detail=ERROR_SITIO_NO_ENCONTRADO
        )

    if not es_propietario(db, sitio_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail=ERROR_SIN_PERMISO
        )

    return update_sitio(
        db,
        sitio_id,
        data,
        current_user.id
    )


@router.delete(
    "/{sitio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar sitio web",
    description="""
## Eliminación de sitio

Permite eliminar un sitio del sistema.

### Seguridad
Solo el propietario puede eliminar el sitio.

### Validaciones
- Existencia del sitio
- Permisos del usuario

### Resultado
El sitio será eliminado permanentemente.
""",
    responses={
        204: {
            "description": "Sitio eliminado correctamente"
        },
        403: {
            "description": "No tienes permisos para eliminar este sitio"
        },
        404: {
            "description": "Sitio no encontrado"
        }
    }
)
def eliminar_sitio(
    sitio_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    sitio = get_sitio(db, sitio_id)

    if not sitio:
        raise HTTPException(
            status_code=404,
            detail=ERROR_SITIO_NO_ENCONTRADO
        )

    if not es_propietario(db, sitio_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail=ERROR_SIN_PERMISO
        )

    delete_sitio(
        db,
        sitio_id,
        current_user.id
    )


@router.post(
    "/{sitio_id}/miniatura",
    summary="Subir miniatura del sitio",
    description="""
## Carga de miniaturas

Permite subir una imagen miniatura personalizada para un sitio.

### Formatos permitidos
- PNG
- JPG
- JPEG
- WEBP

### Funcionalidades
- Generación automática de nombre único
- Almacenamiento asíncrono
- Actualización automática del sitio

### Seguridad
Solo el propietario puede subir imágenes.
""",
    responses={
        200: {
            "description": "Miniatura subida correctamente"
        },
        403: {
            "description": "No tienes permisos para editar este sitio"
        },
        404: {
            "description": "Sitio no encontrado"
        }
    }
)
async def upload_miniatura(
    sitio_id: int,
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    file: Annotated[UploadFile, File(...)]
):
    if not es_propietario(db, sitio_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail=ERROR_SIN_PERMISO
        )

    obj = get_sitio(db, sitio_id)

    if not obj:
        raise HTTPException(
            status_code=404,
            detail=ERROR_SITIO_NO_ENCONTRADO
        )

    file_ext = (
        file.filename.split(".")[-1]
        if "." in file.filename
        else "png"
    )

    if file_ext not in ["png", "jpg", "jpeg", "webp"]:
        file_ext = "png"

    file_name = f"{uuid.uuid4()}.{file_ext}"

    file_path = UPLOAD_DIR / file_name

    # Escritura asíncrona
    content = await file.read()

    await anyio.Path(file_path).write_bytes(content)

    base_url = str(request.base_url).rstrip("/")

    url = f"{base_url}/media/sitios/{file_name}"

    update_sitio(
        db,
        sitio_id,
        SitioUpdate(miniatura=url),
        current_user.id
    )

    return JSONResponse(
        status_code=200,
        content={
            "message": "Miniatura subida correctamente",
            "url": url
        }
    )