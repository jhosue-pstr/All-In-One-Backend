from pydantic import BaseModel


class SitioModuloCreate(BaseModel):
    sitio_id: int
    modulo_id: int


class SitioModuloResponse(BaseModel):
    sitio_id: int
    modulo_id: int

    class Config:
        from_attributes = True