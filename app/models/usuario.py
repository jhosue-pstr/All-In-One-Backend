from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.models.base import BaseModel, TimestampMixin


class User(BaseModel, TimestampMixin):
    __tablename__ = "users"

    correo: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    contraseña: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user")

    sites: Mapped[list["Site"]] = relationship("Site", back_populates="owner", cascade="all, delete-orphan")
