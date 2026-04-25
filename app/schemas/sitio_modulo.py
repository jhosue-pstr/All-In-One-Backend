from pydantic import BaseModel, ConfigDict


class SitioModuloCreate(BaseModel):
    sitio_id: int
    modulo_id: int


class SitioModuloResponse(BaseModel):
    sitio_id: int
    modulo_id: int

    model_config = ConfigDict(from_attributes=True)