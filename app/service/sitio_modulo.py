from sqlalchemy.orm import Session
from app.models.sitio import Sitio
from app.models.modulo import Modulo
from app.models.auditoria import Auditoria  # <-- Importamos la auditoría


def agregar_modulo_a_sitio(db: Session, sitio_id: int, modulo_id: int, user_id: int = None):
    sitio = db.query(Sitio).filter(Sitio.id == sitio_id).first()
    if not sitio:
        return None
    
    modulo = db.query(Modulo).filter(Modulo.id == modulo_id).first()
    if not modulo:
        return None
    
    if modulo not in sitio.modulos:
        sitio.modulos.append(modulo)

        # --- INICIO AUDITORÍA (AGREGAR RELACIÓN) ---
        auditoria = Auditoria(
            entidad="sitio_modulo",
            entidad_id=sitio.id,
            accion="INSERT",
            usuario_id=user_id,
            valores_anteriores=None,
            valores_nuevos={"sitio_id": sitio.id, "modulo_id": modulo.id, "modulo_nombre": modulo.nombre}
        )
        db.add(auditoria)
        # --- FIN AUDITORÍA ---

        db.commit()
    
    return sitio


def quitar_modulo_de_sitio(db: Session, sitio_id: int, modulo_id: int, user_id: int = None):
    sitio = db.query(Sitio).filter(Sitio.id == sitio_id).first()
    if not sitio:
        return None
    
    modulo = db.query(Modulo).filter(Modulo.id == modulo_id).first()
    if not modulo:
        return None
    
    if modulo in sitio.modulos:
        sitio.modulos.remove(modulo)

        # --- INICIO AUDITORÍA (ELIMINAR RELACIÓN) ---
        auditoria = Auditoria(
            entidad="sitio_modulo",
            entidad_id=sitio.id,
            accion="DELETE",
            usuario_id=user_id,
            valores_anteriores={"sitio_id": sitio.id, "modulo_id": modulo.id, "modulo_nombre": modulo.nombre},
            valores_nuevos=None
        )
        db.add(auditoria)
        # --- FIN AUDITORÍA ---

        db.commit()
    
    return sitio


def get_modulos_del_sitio(db: Session, sitio_id: int):
    sitio = db.query(Sitio).filter(Sitio.id == sitio_id).first()
    if not sitio:
        return None
    return sitio.modulos