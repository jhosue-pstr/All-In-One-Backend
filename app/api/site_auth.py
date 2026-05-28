from typing import Annotated

from datetime import (
    datetime,
    timedelta,
    timezone
)

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Query,
    status
)

from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from jose import JWTError, jwt

from app.db.database import get_db

from app.packages.modulos.SiteAuth.models.sitio_usuario import UsuarioSitio

from app.packages.modulos.SiteAuth.schemas.sitio_usuario import (
    UsuarioSitioCreate,
    UsuarioSitioUpdate,
    UsuarioSitioLogin,
    UsuarioSitioResponse,
    TokenResponse,
)

from app.packages.modulos.SiteAuth.services import usuario_sitio as services

from app.core.config import settings
from app.api.auth import get_current_user
from app.models.usuario import User

router = APIRouter(
    prefix="/site-auth",
    tags=[" Site Authentication"]
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/site-auth/login",
    auto_error=False,
    description="JWT Token para autenticación de usuarios del sitio"
)

ERROR_CREDENTIALS = "Could not validate credentials"
ERROR_CORREO_REGISTRADO = "El correo ya esta registrado en este sitio"
ERROR_LOGIN = "Credenciales incorrectas"
ERROR_TOKEN = "Token inválido o expirado"


def get_current_usuario_sitio(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Obtiene el usuario autenticado mediante JWT.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=ERROR_CREDENTIALS,
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token is None:
        raise credentials_exception

    usuario = services.verify_token_usuario_sitio(
        db,
        token
    )

    if usuario is None:
        raise credentials_exception

    return usuario


@router.post(
    "/registro",
    response_model=UsuarioSitioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario del sitio",
    description="""
## Registro de usuarios públicos

Permite registrar usuarios finales dentro de un sitio específico.

### Funcionalidades
- Registro independiente por sitio
- Validación de correo único
- Encriptación automática de contraseña
- Integración con JWT

### Seguridad
Cada usuario queda asociado al sitio correspondiente.

### Resultado
Retorna la información del usuario registrado.
""",
    responses={
        201: {
            "description": "Usuario registrado correctamente"
        },
        400: {
            "description": "El correo ya está registrado en este sitio"
        }
    }
)
def registro(
    user_data: Annotated[UsuarioSitioCreate, Body()],
    db: Annotated[Session, Depends(get_db)]
):
    nuevo_usuario = services.create_usuario_sitio(
        db,
        user_data
    )

    if nuevo_usuario is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_CORREO_REGISTRADO
        )

    return nuevo_usuario


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión en sitio",
    description="""
## Login de usuarios del sitio

Permite autenticar usuarios pertenecientes a un sitio específico.

### Funcionalidades
- Validación de credenciales
- Generación automática de JWT
- Verificación de sitio asociado

### Resultado
Retorna un access token JWT válido.

### Importante
El usuario debe pertenecer al sitio indicado.
""",
    responses={
        200: {
            "description": "Autenticación exitosa"
        },
        401: {
            "description": "Credenciales incorrectas"
        }
    }
)
def login(
    login_data: Annotated[UsuarioSitioLogin, Body()],
    db: Annotated[Session, Depends(get_db)]
):
    usuario = services.authenticate_usuario_sitio(
        db,
        login_data.correo,
        login_data.contrasena,
        login_data.id_sitio
    )

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_LOGIN,
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = services.login_usuario_sitio(
        db,
        usuario
    )

    return TokenResponse(
        access_token=token
    )


@router.post(
    "/logout",
    summary="Cerrar sesión",
    description="""
## Logout de usuario

Finaliza la sesión activa del usuario autenticado.

### Seguridad
Requiere Bearer Token JWT válido.

### Resultado
Invalida la sesión actual del usuario.
""",
    responses={
        200: {
            "description": "Logout realizado correctamente"
        },
        401: {
            "description": "Token inválido"
        }
    }
)
def logout(
    current_user: Annotated[
        UsuarioSitio,
        Depends(get_current_usuario_sitio)
    ],
    db: Annotated[Session, Depends(get_db)]
):
    services.logout_usuario_sitio(
        db,
        current_user
    )

    return {
        "message": "Logout exitoso"
    }


@router.get(
    "/me",
    response_model=UsuarioSitioResponse,
    summary="Obtener perfil del usuario",
    description="""
## Perfil del usuario autenticado

Retorna la información del usuario autenticado mediante JWT.

### Seguridad
Requiere token válido.

### Resultado
Información completa del usuario actual.
""",
    responses={
        200: {
            "description": "Perfil obtenido correctamente"
        },
        401: {
            "description": "Token inválido"
        }
    }
)
def read_me(
    current_user: Annotated[
        UsuarioSitio,
        Depends(get_current_usuario_sitio)
    ],
    db: Annotated[Session, Depends(get_db)]
):
    return current_user


@router.put(
    "/me",
    response_model=UsuarioSitioResponse,
    summary="Actualizar perfil del usuario",
    description="""
## Actualización de perfil

Permite modificar los datos del usuario autenticado.

### Campos editables
- Nombre
- Correo
- Contraseña
- Información personalizada

### Seguridad
Solo el usuario autenticado puede modificar su perfil.

### Resultado
Retorna los datos actualizados.
""",
    responses={
        200: {
            "description": "Perfil actualizado correctamente"
        },
        401: {
            "description": "Token inválido"
        }
    }
)
def update_me(
    user_data: UsuarioSitioUpdate,
    current_user: Annotated[
        UsuarioSitio,
        Depends(get_current_usuario_sitio)
    ],
    db: Annotated[Session, Depends(get_db)]
):
    return services.update_usuario_sitio(
        db,
        current_user,
        user_data
    )


@router.get(
    "/usuarios",
    response_model=list[UsuarioSitioResponse],
    summary="Listar usuarios de un sitio",
)
def listar_usuarios_sitio(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    site_id: int = Query(...),
):
    """Lista todos los usuarios registrados en un sitio específico (admin)"""
    return services.list_usuarios_by_site(db, site_id)


@router.get(
    "/verify",
    summary="Verificar validez de token",
    description="""
## Verificación de JWT

Permite validar si un token JWT sigue siendo válido.

### Funcionalidades
- Verificación de expiración
- Validación criptográfica
- Comprobación de usuario asociado

### Resultado
Retorna el estado del token y datos básicos del usuario.
""",
    responses={
        200: {
            "description": "Token válido"
        },
        401: {
            "description": "Token inválido o expirado"
        }
    }
)
def verify_token(
    token: Annotated[str, Query()],
    db: Annotated[Session, Depends(get_db)]
):
    usuario = services.verify_token_usuario_sitio(
        db,
        token
    )

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_TOKEN
        )

    return {
        "valid": True,
        "usuario_id": usuario.id,
        "id_sitio": usuario.id_sitio
    }