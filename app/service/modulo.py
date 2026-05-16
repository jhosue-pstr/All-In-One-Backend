from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError

from app.models.modulo import Modulo
from app.models.auditoria import Auditoria  # <-- Importamos Auditoria
from app.schemas.modulo import ModuloCreate, ModuloUpdate


def create_modulo(db: Session, data: ModuloCreate, user_id: int = None) -> Modulo:
    modulo = Modulo(**data.model_dump())

    try:
        db.add(modulo)
        db.flush()  # <-- Flush para asegurar que tenemos el ID antes de la auditoría

        # --- INICIO AUDITORÍA (INSERT) ---
        valores_nuevos = jsonable_encoder(modulo)
        auditoria = Auditoria(
            entidad="modulos",
            entidad_id=modulo.id,
            accion="INSERT",
            usuario_id=user_id,
            valores_anteriores=None,
            valores_nuevos=valores_nuevos
        )
        db.add(auditoria)
        # --- FIN AUDITORÍA ---

        db.commit()
        db.refresh(modulo)
        return modulo
    except SQLAlchemyError:
        db.rollback()
        raise


def get_modulo(db: Session, modulo_id: int):
    return db.query(Modulo).filter(Modulo.id == modulo_id).first()


def get_modulos(db: Session):
    return db.query(Modulo).all()


def update_modulo(db: Session, modulo_id: int, data: ModuloUpdate, user_id: int = None):
    obj = get_modulo(db, modulo_id)
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
        entidad="modulos",
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


def delete_modulo(db: Session, modulo_id: int, user_id: int = None):
    obj = get_modulo(db, modulo_id)
    if not obj:
        return None

    # --- INICIO AUDITORÍA (DELETE) ---
    valores_anteriores = jsonable_encoder(obj)
    auditoria = Auditoria(
        entidad="modulos",
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