# app/models/auditoria.py
import enum
from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy import String, Integer, JSON, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class Auditoria(Base):
    __tablename__ = "auditorias_log"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    entidad: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # Nombre de la tabla (sitios, users, plantillas)
    entidad_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)   # ID del registro afectado
    accion: Mapped[str] = mapped_column(String(20), nullable=False, index=True)    # INSERT, UPDATE, DELETE
    usuario_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True) # ID del usuario que hizo el cambio
    valores_anteriores: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    valores_nuevos: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    ip_origen: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)    # Para trazabilidad de red