from typing import Optional, Any
from datetime import datetime
from sqlalchemy import String, ForeignKey, JSON, Boolean, Table, Column, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


sitio_modulos = Table(
    "sitio_modulos",
    Base.metadata,
    Column("sitio_id", ForeignKey("sitios.id", ondelete="CASCADE"), primary_key=True),
    Column("modulo_id", ForeignKey("modulos.id", ondelete="CASCADE"), primary_key=True)
)


class Sitio(Base):
    __tablename__ = "sitios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    nombre: Mapped[str] = mapped_column(String(150), nullable=False)

    slug: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True,
        nullable=False
    )

    id_usuario: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    id_plantilla: Mapped[Optional[int]] = mapped_column(
        ForeignKey("plantillas.id", ondelete="SET NULL"),
        nullable=True
    )

    configuracion: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    switches: Mapped[Optional[dict[str, bool]]] = mapped_column(JSON, nullable=True)

    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    modulos: Mapped[list["Modulo"]] = relationship(
        "Modulo",
        secondary=sitio_modulos,
        backref="sitios"
    )