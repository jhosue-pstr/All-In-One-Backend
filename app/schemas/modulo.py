from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ModuloBase(BaseModel):
    nombre: str
    slug: str
    descripcion: Optional[str] = None
    tipo: str
    configuracion_base: Optional[dict[str, Any]] = None
    activo: Optional[bool] = True


class ModuloCreate(ModuloBase):
    pass


class ModuloUpdate(BaseModel):
    nombre: Optional[str] = None
    slug: Optional[str] = None
    descripcion: Optional[str] = None
    tipo: Optional[str] = None
    configuracion_base: Optional[dict[str, Any]] = None
    activo: Optional[bool] = None


class ModuloResponse(ModuloBase):
    id: int

    model_config = ConfigDict(from_attributes=True)