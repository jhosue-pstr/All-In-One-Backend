from typing import Optional, Any
from enum import Enum
from sqlalchemy import String, Boolean, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base   


class Visibilidad(str, Enum):
    PUBLICA = "PUBLICA"
    PRIVADA = "PRIVADA"


class Plantilla(Base): 
    __tablename__ = "plantillas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)   
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )

    descripcion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    configuracion: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    miniatura: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    visibilidad: Mapped[Visibilidad] = mapped_column(
        SQLEnum(Visibilidad),
        default=Visibilidad.PRIVADA,
        nullable=False
    )

    id_usuario: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)