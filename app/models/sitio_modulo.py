from sqlalchemy import Column, Integer, ForeignKey
from app.db.database import Base


class SitioModulo(Base):
    __tablename__ = "sitio_modulos"

    sitio_id: int = Column(
        ForeignKey("sitios.id", ondelete="CASCADE"),
        primary_key=True
    )
    modulo_id: int = Column(
        ForeignKey("modulos.id", ondelete="CASCADE"),
        primary_key=True
    )