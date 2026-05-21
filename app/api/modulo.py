from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

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

router = APIRouter(
    prefix="/modulos",
    tags=["Gestión de Módulos"]
)

ERROR_MODULO_NO_ENCONTRADO = "Modulo no encontrado"


@router.post(
    "/",
    response_model=ModuloResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo módulo",
    description="""
## Creación de módulos

Permite registrar un nuevo módulo dentro del sistema.

### Funcionalidades
- Registro persistente en base de datos
- Asociación automática con el usuario creador
- Compatible con el sistema SaaS modular

### Seguridad
Requiere autenticación JWT válida.

### Resultado
Retorna la información completa del módulo creado.
""",
    responses={
        201: {
            "description": "Módulo creado correctamente"
        },
        401: {
            "description": "Usuario no autenticado"
        }
    }
)
def crear_modulo(
    data: ModuloCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    return create_modulo(
        db,
        data,
        current_user.id
    )


@router.get(
    "/",
    response_model=list[ModuloResponse],
    summary="Listar módulos",
    description="""
## Listado de módulos

Obtiene todos los módulos registrados en el sistema.

### Información retornada
- Nombre del módulo
- Configuración
- Estado
- Datos asociados

### Uso común
- Dashboard administrativo
- Panel modular
- Constructor dinámico
""",
    responses={
        200: {
            "description": "Lista de módulos obtenida correctamente"
        }
    }
)
def listar_modulos(
    db: Annotated[Session, Depends(get_db)]
):
    return get_modulos(db)


@router.get(
    "/{modulo_id}",
    response_model=ModuloResponse,
    summary="Obtener módulo por ID",
    description="""
## Consulta individual de módulo

Permite obtener la información detallada de un módulo específico.

### Parámetros
- modulo_id: identificador único del módulo

### Resultado
Retorna toda la información del módulo solicitado.
""",
    responses={
        200: {
            "description": "Módulo encontrado correctamente"
        },
        404: {
            "description": "Módulo no encontrado"
        }
    }
)
def obtener_modulo(
    modulo_id: int,
    db: Annotated[Session, Depends(get_db)]
):
    modulo = get_modulo(db, modulo_id)

    if not modulo:
        raise HTTPException(
            status_code=404,
            detail=ERROR_MODULO_NO_ENCONTRADO
        )

    return modulo


@router.put(
    "/{modulo_id}",
    response_model=ModuloResponse,
    summary="Actualizar módulo",
    description="""
## Modificación de módulos

Permite actualizar la configuración y datos de un módulo existente.

### Funcionalidades
- Actualización parcial o completa
- Persistencia automática
- Validación de existencia

### Seguridad
Requiere autenticación JWT.

### Resultado
Retorna el módulo actualizado.
""",
    responses={
        200: {
            "description": "Módulo actualizado correctamente"
        },
        404: {
            "description": "Módulo no encontrado"
        },
        401: {
            "description": "Usuario no autenticado"
        }
    }
)
def actualizar_modulo(
    modulo_id: int,
    data: ModuloUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    modulo = get_modulo(db, modulo_id)

    if not modulo:
        raise HTTPException(
            status_code=404,
            detail=ERROR_MODULO_NO_ENCONTRADO
        )

    return update_modulo(
        db,
        modulo_id,
        data,
        current_user.id
    )


@router.delete(
    "/{modulo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar módulo",
    description="""
## Eliminación de módulos

Permite eliminar un módulo del sistema.

### Validaciones
- Verificación de existencia
- Validación de autenticación

### Seguridad
Solo usuarios autenticados pueden realizar esta acción.

### Resultado
El módulo será eliminado permanentemente.
""",
    responses={
        204: {
            "description": "Módulo eliminado correctamente"
        },
        404: {
            "description": "Módulo no encontrado"
        },
        401: {
            "description": "Usuario no autenticado"
        }
    }
)
def eliminar_modulo(
    modulo_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    modulo = get_modulo(db, modulo_id)

    if not modulo:
        raise HTTPException(
            status_code=404,
            detail=ERROR_MODULO_NO_ENCONTRADO
        )

    delete_modulo(
        db,
        modulo_id,
        current_user.id
    )