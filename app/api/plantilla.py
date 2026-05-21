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

from app.schemas.plantilla import (
    PlantillaCreate,
    PlantillaUpdate,
    PlantillaResponse
)

from app.service.plantilla import (
    create_plantilla,
    get_plantilla,
    get_plantillas_publicas,
    get_plantillas_del_usuario,
    update_plantilla,
    delete_plantilla,
    es_propietario,
)

from app.api.auth import get_current_user
from app.models.usuario import User
from app.models.plantilla import Visibilidad

router = APIRouter(
    prefix="/plantillas",
    tags=["Gestión de Plantillas"]
)

UPLOAD_DIR = Path("media/plantillas")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ERROR_PLANTILLA_NO_ENCONTRADA = "Plantilla no encontrada"
ERROR_SIN_PERMISO = "No tienes permiso para editar esta plantilla"
ERROR_SIN_PERMISO_ELIMINAR = "No tienes permiso para eliminar esta plantilla"


@router.get(
    "/publicas",
    response_model=list[PlantillaResponse],
    summary="Obtener plantillas públicas",
    description="""
## Listado de plantillas públicas

Retorna todas las plantillas configuradas como públicas dentro del sistema.

### Información incluida
- Nombre de plantilla
- Miniatura
- Configuración visual
- Datos asociados

### Uso común
- Marketplace de plantillas
- Catálogo visual
- Explorador de diseños
""",
    responses={
        200: {
            "description": "Plantillas públicas obtenidas correctamente"
        }
    }
)
def get_publicas(
    db: Annotated[Session, Depends(get_db)]
):
    return get_plantillas_publicas(db)


@router.get(
    "/mis-plantillas",
    response_model=list[PlantillaResponse],
    summary="Obtener mis plantillas",
    description="""
## Plantillas del usuario autenticado

Retorna únicamente las plantillas creadas por el usuario actual.

### Seguridad
Requiere autenticación JWT válida.

### Resultado
Listado personalizado de plantillas privadas y públicas del usuario.
""",
    responses={
        200: {
            "description": "Plantillas del usuario obtenidas correctamente"
        },
        401: {
            "description": "Usuario no autenticado"
        }
    }
)
def get_mis_plantillas(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    return get_plantillas_del_usuario(
        db,
        current_user.id
    )


@router.get(
    "",
    response_model=list[PlantillaResponse],
    summary="Obtener todas las plantillas accesibles",
    description="""
## Catálogo completo de plantillas

Obtiene:
- Plantillas públicas
- Plantillas del usuario autenticado

### Funcionalidad
Fusiona automáticamente ambas listas.

### Uso común
- Dashboard principal
- Explorador de diseños
- Sistema drag & drop
""",
    responses={
        200: {
            "description": "Listado completo obtenido correctamente"
        },
        401: {
            "description": "Usuario no autenticado"
        }
    }
)
def get_all(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    publicas = get_plantillas_publicas(db)

    mias = get_plantillas_del_usuario(
        db,
        current_user.id
    )

    return publicas + mias


@router.get(
    "/{plantilla_id}",
    response_model=PlantillaResponse,
    summary="Obtener plantilla por ID",
    description="""
## Consulta individual de plantilla

Obtiene toda la información detallada de una plantilla específica.

### Parámetros
- plantilla_id: identificador único de la plantilla

### Resultado
Información completa de la plantilla solicitada.
""",
    responses={
        200: {
            "description": "Plantilla encontrada correctamente"
        },
        404: {
            "description": "Plantilla no encontrada"
        }
    }
)
def get_one(
    plantilla_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    obj = get_plantilla(db, plantilla_id)

    if not obj:
        raise HTTPException(
            status_code=404,
            detail=ERROR_PLANTILLA_NO_ENCONTRADA
        )

    return obj


@router.post(
    "",
    response_model=PlantillaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva plantilla",
    description="""
## Registro de plantillas

Permite crear una nueva plantilla visual dentro del sistema.

### Funcionalidades
- Asociación automática con el usuario creador
- Configuración inicial persistente
- Compatible con constructor drag & drop

### Seguridad
Requiere autenticación JWT válida.

### Resultado
Retorna la plantilla creada.
""",
    responses={
        201: {
            "description": "Plantilla creada correctamente"
        },
        401: {
            "description": "Usuario no autenticado"
        }
    }
)
def create(
    data: PlantillaCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    return create_plantilla(
        db,
        data,
        current_user.id
    )


@router.put(
    "/{plantilla_id}",
    response_model=PlantillaResponse,
    summary="Actualizar plantilla",
    description="""
## Modificación de plantillas

Permite actualizar la configuración y contenido de una plantilla existente.

### Seguridad
Solo el propietario puede modificar la plantilla.

### Validaciones
- Existencia de plantilla
- Permisos del usuario autenticado

### Resultado
Retorna la plantilla actualizada.
""",
    responses={
        200: {
            "description": "Plantilla actualizada correctamente"
        },
        403: {
            "description": "No tienes permisos para editar esta plantilla"
        },
        404: {
            "description": "Plantilla no encontrada"
        }
    }
)
def update(
    plantilla_id: int,
    data: PlantillaUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    if not es_propietario(
        db,
        plantilla_id,
        current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail=ERROR_SIN_PERMISO
        )

    obj = update_plantilla(
        db,
        plantilla_id,
        data,
        current_user.id
    )

    if not obj:
        raise HTTPException(
            status_code=404,
            detail=ERROR_PLANTILLA_NO_ENCONTRADA
        )

    return obj


@router.delete(
    "/{plantilla_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar plantilla",
    description="""
## Eliminación de plantillas

Permite eliminar una plantilla registrada en el sistema.

### Seguridad
Solo el propietario puede eliminar la plantilla.

### Validaciones
- Verificación de permisos
- Validación de existencia

### Resultado
La plantilla será eliminada permanentemente.
""",
    responses={
        200: {
            "description": "Plantilla eliminada correctamente"
        },
        403: {
            "description": "No tienes permisos para eliminar esta plantilla"
        }
    }
)
def delete(
    plantilla_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    if not es_propietario(
        db,
        plantilla_id,
        current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail=ERROR_SIN_PERMISO_ELIMINAR
        )

    delete_plantilla(
        db,
        plantilla_id,
        current_user.id
    )

    return {
        "message": "Plantilla eliminada correctamente"
    }


@router.post(
    "/{plantilla_id}/miniatura",
    summary="Subir miniatura de plantilla",
    description="""
## Carga de miniaturas

Permite subir una imagen personalizada para representar visualmente una plantilla.

### Formatos soportados
- PNG
- JPG
- JPEG
- WEBP

### Funcionalidades
- Generación automática de nombres únicos
- Escritura asíncrona de archivos
- Actualización automática de URL

### Seguridad
Solo el propietario puede subir miniaturas.
""",
    responses={
        200: {
            "description": "Miniatura subida correctamente"
        },
        403: {
            "description": "No tienes permisos para editar esta plantilla"
        },
        404: {
            "description": "Plantilla no encontrada"
        }
    }
)
async def upload_miniatura(
    plantilla_id: int,
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    file: Annotated[UploadFile, File(...)]
):
    if not es_propietario(
        db,
        plantilla_id,
        current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail=ERROR_SIN_PERMISO
        )

    obj = get_plantilla(
        db,
        plantilla_id
    )

    if not obj:
        raise HTTPException(
            status_code=404,
            detail=ERROR_PLANTILLA_NO_ENCONTRADA
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

    url = f"{base_url}/media/plantillas/{file_name}"

    update_plantilla(
        db,
        plantilla_id,
        PlantillaUpdate(miniatura=url),
        current_user.id
    )

    return JSONResponse(
        status_code=200,
        content={
            "message": "Miniatura subida correctamente",
            "url": url
        }
    )


# EOF FIX
_eof_bug_fix = True