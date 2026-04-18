from sqlalchemy.orm import Session
from app.models.sitio import Sitio
from app.models.modulo import Modulo


def agregar_modulo_a_sitio(db: Session, sitio_id: int, modulo_id: int):
    sitio = db.query(Sitio).filter(Sitio.id == sitio_id).first()
    if not sitio:
        return None
    
    modulo = db.query(Modulo).filter(Modulo.id == modulo_id).first()
    if not modulo:
        return None
    
    if modulo not in sitio.modulos:
        sitio.modulos.append(modulo)
        db.commit()
    
    return sitio


def quitar_modulo_de_sitio(db: Session, sitio_id: int, modulo_id: int):
    sitio = db.query(Sitio).filter(Sitio.id == sitio_id).first()
    if not sitio:
        return None
    
    modulo = db.query(Modulo).filter(Modulo.id == modulo_id).first()
    if not modulo:
        return None
    
    if modulo in sitio.modulos:
        sitio.modulos.remove(modulo)
        db.commit()
    
    return sitio


def get_modulos_del_sitio(db: Session, sitio_id: int):
    sitio = db.query(Sitio).filter(Sitio.id == sitio_id).first()
    if not sitio:
        return None
    return sitio.modulos