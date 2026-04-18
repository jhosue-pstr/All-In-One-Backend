from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class SitioBase(BaseModel):
    nombre: str
    slug: str
    id_usuario: Optional[int] = None
    id_plantilla: Optional[int] = None
    configuracion: Optional[dict[str, Any]] = None
    switches: Optional[dict[str, bool]] = None
    activo: Optional[bool] = True


class SitioCreate(SitioBase):
    pass


class SitioUpdate(BaseModel):
    nombre: Optional[str] = None
    slug: Optional[str] = None
    id_usuario: Optional[int] = None
    id_plantilla: Optional[int] = None
    configuracion: Optional[dict[str, Any]] = None
    switches: Optional[dict[str, bool]] = None
    activo: Optional[bool] = None


class SitioResponse(SitioBase):
    id: int

    model_config = ConfigDict(from_attributes=True)