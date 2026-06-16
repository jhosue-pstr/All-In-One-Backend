from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, Text, DateTime, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models.base import BaseModel, TimestampMixin


class Visita(BaseModel, TimestampMixin):
    __tablename__ = "analitica_visitas"

    site_id: Mapped[int] = mapped_column(Integer, ForeignKey("sitios.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    titulo_pagina: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    referer: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    pais: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    navegador: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    dispositivo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)


class Evento(BaseModel, TimestampMixin):
    __tablename__ = "analitica_eventos"

    site_id: Mapped[int] = mapped_column(Integer, ForeignKey("sitios.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tipo: Mapped[str] = mapped_column(String(100), nullable=False)
    etiqueta: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    valor: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)


class Sesion(BaseModel, TimestampMixin):
    __tablename__ = "analitica_sesiones"

    site_id: Mapped[int] = mapped_column(Integer, ForeignKey("sitios.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fin: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    paginas_vistas: Mapped[int] = mapped_column(Integer, default=1)
    duracion_segundos: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
