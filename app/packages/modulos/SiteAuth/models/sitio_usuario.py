from datetime import datetime
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.models.base import BaseModel, TimestampMixin


class UsuarioSitio(BaseModel, TimestampMixin):
    __tablename__ = "usuarios_sitio"

    id_sitio: Mapped[int] = mapped_column(
        ForeignKey("sitios.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    correo: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    contrasena: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    token: Mapped[str | None] = mapped_column(Text, nullable=True)