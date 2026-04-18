from typing import Optional, Any
from pydantic import BaseModel, ConfigDict
from app.models.plantilla import Visibilidad


class PlantillaBase(BaseModel):
    nombre: str
    slug: str
    descripcion: Optional[str] = None
    configuracion: Optional[dict[str, Any]] = None
    miniatura: Optional[str] = None
    activo: Optional[bool] = True
    visibilidad: Optional[Visibilidad] = Visibilidad.PRIVADA


class PlantillaCreate(PlantillaBase):
    pass


class PlantillaUpdate(BaseModel):
    nombre: Optional[str] = None
    slug: Optional[str] = None
    descripcion: Optional[str] = None
    configuracion: Optional[dict[str, Any]] = None
    miniatura: Optional[str] = None
    activo: Optional[bool] = None
    visibilidad: Optional[Visibilidad] = None


class PlantillaResponse(PlantillaBase):
    id: int
    id_usuario: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)