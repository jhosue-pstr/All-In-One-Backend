from pydantic import BaseModel, EmailStr
from typing import Optional


class PermisoResponse(BaseModel):
    id: int
    nombre: str
    codigo: str
    modulo: str
    descripcion: Optional[str] = None
    activo: bool

    class Config:
        from_attributes = True


class RolCreate(BaseModel):
    nombre: str
    codigo: str
    descripcion: Optional[str] = None
    permisos: list[str] = []


class RolUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None
    permisos: Optional[list[str]] = None


class RolResponse(BaseModel):
    id: int
    nombre: str
    codigo: str
    descripcion: Optional[str] = None
    activo: bool
    es_sistema: bool
    permisos: list[str] = []

    class Config:
        from_attributes = True


class UsuarioSistemaCreate(BaseModel):
    correo: EmailStr
    contrasena: str
    nombre: str
    apellido: str
    role: str


class UsuarioSistemaResponse(BaseModel):
    id: int
    correo: EmailStr
    nombre: str
    apellido: str
    role: str
    activo: bool

    class Config:
        from_attributes = True


class CambiarRolUsuario(BaseModel):
    role: str