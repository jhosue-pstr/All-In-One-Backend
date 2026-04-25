from typing import Annotated
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
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

router = APIRouter(prefix="/site-auth", tags=["site-auth"])


def get_current_usuario_sitio(
    token: str,
    db: Annotated[Session, Depends(get_db)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    usuario = services.verify_token_usuario_sitio(db, token)
    if usuario is None:
        raise credentials_exception
    return usuario


@router.post("/registro", response_model=UsuarioSitioResponse, status_code=status.HTTP_201_CREATED)
def registro(
    user_data: Annotated[UsuarioSitioCreate, Body()],
    db: Annotated[Session, Depends(get_db)]
):
    nuevo_usuario = services.create_usuario_sitio(db, user_data)
    if nuevo_usuario is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya esta registrado en este sitio"
        )
    return nuevo_usuario


@router.post("/login", response_model=TokenResponse)
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
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = services.login_usuario_sitio(db, usuario)
    return TokenResponse(access_token=token)


@router.post("/logout")
def logout(
    current_user: Annotated[UsuarioSitio, Depends(get_current_usuario_sitio)],
    db: Annotated[Session, Depends(get_db)]
):
    services.logout_usuario_sitio(db, current_user)
    return {"message": "Logout exitoso"}


@router.get("/me", response_model=UsuarioSitioResponse)
def read_me(
    current_user: Annotated[UsuarioSitio, Depends(get_current_usuario_sitio)],
    db: Annotated[Session, Depends(get_db)]
):
    return current_user


@router.put("/me", response_model=UsuarioSitioResponse)
def update_me(
    user_data: UsuarioSitioUpdate,
    current_user: Annotated[UsuarioSitio, Depends(get_current_usuario_sitio)],
    db: Annotated[Session, Depends(get_db)]
):
    return services.update_usuario_sitio(db, current_user, user_data)


@router.get("/verify")
def verify_token(
    token: Annotated[str, Query()],
    db: Annotated[Session, Depends(get_db)]
):
    usuario = services.verify_token_usuario_sitio(db, token)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    return {"valid": True, "usuario_id": usuario.id, "id_sitio": usuario.id_sitio}