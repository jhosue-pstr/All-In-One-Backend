from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

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

router = APIRouter(
    prefix="/sitios/{sitio_id}/modulos",
    tags=["Sitio - Módulos"]
)

ERROR_SITIO_NO_ENCONTRADO = "Sitio no encontrado"

ERROR_SITIO_O_MODULO_NO_ENCONTRADO = (
    "Sitio o Modulo no encontrado"
)

ERROR_SIN_PERMISO = (
    "No tienes permiso para modificar los módulos de este sitio"
)


def es_propietario_sitio(
    db: Session,
    sitio_id: int,
    usuario_id: int
):
    """
    Verifica si el usuario autenticado
    es propietario del sitio.
    """

    sitio = (
        db.query(Sitio)
        .filter(Sitio.id == sitio_id)
        .first()
    )

    if not sitio:
        return False

    return sitio.id_usuario == usuario_id


@router.get(
    "/",
    response_model=list[int],
    summary="Listar módulos del sitio",
    description="""
## Obtener módulos asociados a un sitio

Retorna la lista de módulos vinculados a un sitio específico.

### Información retornada
- IDs de módulos asociados
- Relaciones activas del sitio

### Uso común
- Constructor dinámico
- Sistema modular
- Configuración visual del sitio

### Resultado
Lista de identificadores de módulos.
""",
    responses={
        200: {
            "description": "Módulos obtenidos correctamente"
        },
        404: {
            "description": "Sitio no encontrado"
        }
    }
)
def listar_modulos(
    sitio_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    sitio = (
        db.query(Sitio)
        .filter(Sitio.id == sitio_id)
        .first()
    )

    if not sitio:
        raise HTTPException(
            status_code=404,
            detail=ERROR_SITIO_NO_ENCONTRADO
        )

    return [m.id for m in sitio.modulos]


@router.post(
    "/{modulo_id}",
    summary="Agregar módulo a sitio",
    description="""
## Asociación de módulos

Permite agregar un módulo a un sitio específico.

### Funcionalidades
- Vinculación dinámica de módulos
- Asociación persistente en base de datos
- Compatible con sistema drag & drop

### Seguridad
Solo el propietario del sitio puede realizar esta acción.

### Validaciones
- Existencia del sitio
- Existencia del módulo
- Permisos del usuario autenticado

### Resultado
El módulo quedará asociado al sitio.
""",
    responses={
        200: {
            "description": "Módulo agregado correctamente"
        },
        403: {
            "description": "No tienes permisos para modificar este sitio"
        },
        404: {
            "description": "Sitio o módulo no encontrado"
        }
    }
)
def agregar_modulo(
    sitio_id: int,
    modulo_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    # Validar propiedad del sitio
    if not es_propietario_sitio(
        db,
        sitio_id,
        current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail=ERROR_SIN_PERMISO
        )

    sitio = agregar_modulo_a_sitio(
        db,
        sitio_id,
        modulo_id,
        current_user.id
    )

    if not sitio:
        raise HTTPException(
            status_code=404,
            detail=ERROR_SITIO_O_MODULO_NO_ENCONTRADO
        )

    return {
        "message": "Modulo agregado correctamente"
    }


@router.delete(
    "/{modulo_id}",
    summary="Quitar módulo del sitio",
    description="""
## Eliminación de asociaciones

Permite remover un módulo previamente asociado a un sitio.

### Funcionalidades
- Eliminación de relación sitio-módulo
- Persistencia automática
- Actualización dinámica del sitio

### Seguridad
Solo el propietario puede modificar los módulos del sitio.

### Validaciones
- Existencia del sitio
- Existencia del módulo
- Validación de permisos

### Resultado
El módulo será removido del sitio.
""",
    responses={
        200: {
            "description": "Módulo removido correctamente"
        },
        403: {
            "description": "No tienes permisos para modificar este sitio"
        },
        404: {
            "description": "Sitio o módulo no encontrado"
        }
    }
)
def quitar_modulo(
    sitio_id: int,
    modulo_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    # Validar propiedad del sitio
    if not es_propietario_sitio(
        db,
        sitio_id,
        current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail=ERROR_SIN_PERMISO
        )

    sitio = quitar_modulo_de_sitio(
        db,
        sitio_id,
        modulo_id,
        current_user.id
    )

    if not sitio:
        raise HTTPException(
            status_code=404,
            detail=ERROR_SITIO_O_MODULO_NO_ENCONTRADO
        )

    return {
        "message": "Modulo removido correctamente"
    }