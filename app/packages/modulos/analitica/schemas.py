from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from datetime import datetime


class VisitaCreate(BaseModel):
    url: str = Field(..., max_length=500)
    titulo_pagina: Optional[str] = Field(None, max_length=255)
    referer: Optional[str] = Field(None, max_length=500)
    session_id: Optional[str] = Field(None, max_length=100)


class VisitaResponse(BaseModel):
    id: int
    site_id: int
    url: str
    titulo_pagina: Optional[str]
    ip: Optional[str]
    user_agent: Optional[str]
    referer: Optional[str]
    session_id: Optional[str]
    navegador: Optional[str]
    dispositivo: Optional[str]
    pais: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventoCreate(BaseModel):
    tipo: str = Field(..., max_length=100)
    etiqueta: Optional[str] = Field(None, max_length=255)
    valor: Optional[str] = Field(None, max_length=255)
    metadata_json: Optional[Any] = None
    url: Optional[str] = Field(None, max_length=500)
    session_id: Optional[str] = Field(None, max_length=100)


class EventoResponse(BaseModel):
    id: int
    site_id: int
    tipo: str
    etiqueta: Optional[str]
    valor: Optional[str]
    metadata_json: Optional[Any]
    url: Optional[str]
    session_id: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumenAnalitica(BaseModel):
    visitas_hoy: int
    visitas_7d: int
    visitas_30d: int
    visitantes_unicos: int
    bounce_rate: float
    duracion_promedio: float
    total_visitas: int
    total_eventos: int


class TopPagina(BaseModel):
    url: str
    visitas: int
    porcentaje: float


class VisitaPorDia(BaseModel):
    fecha: str
    visitas: int


class DashboardResponse(BaseModel):
    resumen: ResumenAnalitica
    visitas_por_dia: list[VisitaPorDia]
    top_paginas: list[TopPagina]
    navegadores: dict[str, int]
    dispositivos: dict[str, int]
    ultimas_visitas: list[VisitaResponse]
    eventos_recientes: list[EventoResponse]
