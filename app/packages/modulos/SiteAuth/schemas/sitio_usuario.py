from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr


class UsuarioSitioBase(BaseModel):
    correo: EmailStr
    nombre: str
    apellido: str
    id_sitio: int


class UsuarioSitioCreate(UsuarioSitioBase):
    contrasena: str


class UsuarioSitioUpdate(BaseModel):
    nombre: str | None = None
    apellido: str | None = None
    contrasena: str | None = None


class UsuarioSitioLogin(BaseModel):
    correo: EmailStr
    contrasena: str
    id_sitio: int


class UsuarioSitioResponse(UsuarioSitioBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    usuario_id: int | None = None
    id_sitio: int | None = None