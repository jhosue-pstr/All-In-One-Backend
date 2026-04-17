from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class PlantillaBase(BaseModel):
    nombre: str
    slug: str
    descripcion: Optional[str] = None
    configuracion: Optional[dict[str, Any]] = None
    miniatura: Optional[str] = None
    activo: Optional[bool] = True


class PlantillaCreate(PlantillaBase):
    pass


class PlantillaUpdate(BaseModel):
    nombre: Optional[str] = None
    slug: Optional[str] = None
    descripcion: Optional[str] = None
    configuracion: Optional[dict[str, Any]] = None
    miniatura: Optional[str] = None
    activo: Optional[bool] = None


class PlantillaResponse(PlantillaBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)