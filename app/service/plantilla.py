from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.models.plantilla import Plantilla, Visibilidad
from app.models.auditoria import Auditoria  # <-- Importamos Auditoria
from app.schemas.plantilla import PlantillaCreate, PlantillaUpdate


def create_plantilla(db: Session, data: PlantillaCreate, user_id: int = None):
    obj_data = data.model_dump()
    if user_id:
        obj_data["id_usuario"] = user_id
    obj = Plantilla(**obj_data)
    db.add(obj)
    db.flush()  # <-- Flush para obtener el ID generado sin cerrar transacción

    # --- INICIO AUDITORÍA (INSERT) ---
    valores_nuevos = jsonable_encoder(obj)
    auditoria = Auditoria(
        entidad="plantillas",
        entidad_id=obj.id,
        accion="INSERT",
        usuario_id=user_id,
        valores_anteriores=None,
        valores_nuevos=valores_nuevos
    )
    db.add(auditoria)
    # --- FIN AUDITORÍA ---

    db.commit()
    db.refresh(obj)
    return obj


def get_plantilla(db: Session, plantilla_id: int):
    return db.query(Plantilla).filter(Plantilla.id == plantilla_id).first()


def get_plantillas(db: Session):
    return db.query(Plantilla).all()


def get_plantillas_publicas(db: Session):
    return db.query(Plantilla).filter(Plantilla.visibilidad == Visibilidad.PUBLICA).all()


def get_plantillas_del_usuario(db: Session, user_id: int):
    return (
        db.query(Plantilla)
        .filter(Plantilla.id_usuario == user_id)
        .order_by(Plantilla.id.desc())
        .all()
    )

# <-- Añadimos user_id opcional
def update_plantilla(db: Session, plantilla_id: int, data: PlantillaUpdate, user_id: int = None):
    obj = get_plantilla(db, plantilla_id)
    if not obj:
        return None

    # --- INICIO AUDITORÍA (CAPTURA ANTES) ---
    valores_anteriores = jsonable_encoder(obj)
    # --- FIN CAPTURA ANTES ---

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)

    # --- INICIO AUDITORÍA (UPDATE) ---
    valores_nuevos = jsonable_encoder(obj)
    auditoria = Auditoria(
        entidad="plantillas",
        entidad_id=obj.id,
        accion="UPDATE",
        usuario_id=user_id,
        valores_anteriores=valores_anteriores,
        valores_nuevos=valores_nuevos
    )
    db.add(auditoria)
    # --- FIN AUDITORÍA ---

    db.commit()
    db.refresh(obj)
    return obj


# <-- Añadimos user_id opcional
def delete_plantilla(db: Session, plantilla_id: int, user_id: int = None):
    obj = get_plantilla(db, plantilla_id)
    if not obj:
        return None

    # --- INICIO AUDITORÍA (DELETE) ---
    valores_anteriores = jsonable_encoder(obj)
    auditoria = Auditoria(
        entidad="plantillas",
        entidad_id=obj.id,
        accion="DELETE",
        usuario_id=user_id,
        valores_anteriores=valores_anteriores,
        valores_nuevos=None
    )
    db.add(auditoria)
    # --- FIN AUDITORÍA ---

    db.delete(obj)
    db.commit()


def es_propietario(db: Session, plantilla_id: int, user_id: int) -> bool:
    obj = get_plantilla(db, plantilla_id)
    return obj and obj.id_usuario == user_id