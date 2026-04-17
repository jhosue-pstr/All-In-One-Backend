from typing import Optional, Any
from datetime import datetime
from sqlalchemy import String, Boolean, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base   

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

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)