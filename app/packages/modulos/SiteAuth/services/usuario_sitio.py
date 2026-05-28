from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
import bcrypt
from jose import JWTError, jwt

from app.packages.modulos.SiteAuth.models.sitio_usuario import UsuarioSitio
from app.packages.modulos.SiteAuth.schemas.sitio_usuario import (
    UsuarioSitioCreate,
    UsuarioSitioUpdate,
    UsuarioSitioLogin,
)
from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def authenticate_usuario_sitio(db: Session, correo: str, contrasena: str, id_sitio: int):
    # FILTRO SOFT DELETE
    usuario = db.query(UsuarioSitio).filter(
        UsuarioSitio.correo == correo,
        UsuarioSitio.id_sitio == id_sitio,
        UsuarioSitio.activo == True
    ).first()
    if not usuario:
        return None
    if not verify_password(contrasena, usuario.contrasena):
        return None
    return usuario


def create_usuario_sitio(db: Session, user_data: UsuarioSitioCreate):
    existing = db.query(UsuarioSitio).filter(
        UsuarioSitio.correo == user_data.correo
    ).first()
    if existing:
        return None

    hashed_password = get_password_hash(user_data.contrasena)
    nuevo_usuario = UsuarioSitio(
        id_sitio=user_data.id_sitio,
        correo=user_data.correo,
        contrasena=hashed_password,
        nombre=user_data.nombre,
        apellido=user_data.apellido,
        telefono=user_data.telefono,
        direccion_envio=user_data.direccion_envio,
        ciudad=user_data.ciudad,
        pais=user_data.pais,
        codigo_postal=user_data.codigo_postal
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


def update_usuario_sitio(db: Session, usuario: UsuarioSitio, user_data: UsuarioSitioUpdate):
    if user_data.nombre is not None:
        usuario.nombre = user_data.nombre
    if user_data.apellido is not None:
        usuario.apellido = user_data.apellido
    if user_data.contrasena is not None:
        usuario.contrasena = get_password_hash(user_data.contrasena)
    if user_data.telefono is not None:
        usuario.telefono = user_data.telefono
    if user_data.direccion_envio is not None:
        usuario.direccion_envio = user_data.direccion_envio
    if user_data.ciudad is not None:
        usuario.ciudad = user_data.ciudad
    if user_data.pais is not None:
        usuario.pais = user_data.pais
    if user_data.codigo_postal is not None:
        usuario.codigo_postal = user_data.codigo_postal

    db.commit()
    db.refresh(usuario)
    return usuario


def login_usuario_sitio(db: Session,usuario: UsuarioSitio):
    token = create_access_token(data={"sub": str(usuario.id), "sitio": str(usuario.id_sitio)})
    usuario.token = token
    db.commit()
    db.refresh(usuario)
    return token


def logout_usuario_sitio(db: Session, usuario: UsuarioSitio):
    usuario.token = None
    db.commit()
    return True


def verify_token_usuario_sitio(db: Session, token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        usuario_id = payload.get("sub")
        if usuario_id is None:
            return None
        usuario_id = int(usuario_id)
    except JWTError:
        return None

    # FILTRO SOFT DELETE
    usuario = db.query(UsuarioSitio).filter(
        UsuarioSitio.id == usuario_id, 
        UsuarioSitio.activo == True
    ).first()
    
    if usuario is None or usuario.token != token:
        return None
    return usuario


def get_usuario_by_id(db: Session, usuario_id: int):
    # FILTRO SOFT DELETE
    return db.query(UsuarioSitio).filter(
        UsuarioSitio.id == usuario_id, 
        UsuarioSitio.activo == True
    ).first()


def list_usuarios_by_site(db: Session, site_id: int):
    return db.query(UsuarioSitio).filter(
        UsuarioSitio.id_sitio == site_id
    ).order_by(UsuarioSitio.created_at.desc()).all()
