from typing import Optional, Any
from sqlalchemy import String, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Modulo(Base):
    __tablename__ = "modulos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255))
    tipo: Mapped[str] = mapped_column(String(50))
    configuracion_base: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)