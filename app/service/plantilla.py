from sqlalchemy.orm import Session
from app.models.plantilla import Plantilla, Visibilidad
from app.schemas.plantilla import PlantillaCreate, PlantillaUpdate


def create_plantilla(db: Session, data: PlantillaCreate, user_id: int = None):
    obj_data = data.model_dump()
    if user_id:
        obj_data["id_usuario"] = user_id
    obj = Plantilla(**obj_data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_plantilla(db: Session, plantilla_id: int):
    return db.query(Plantilla).filter(Plantilla.id == plantilla_id).first()


def get_plantillas(db: Session, user_id: int = None):
    return db.query(Plantilla).all()


def get_plantillas_publicas(db: Session):
    return db.query(Plantilla).filter(Plantilla.visibilidad == Visibilidad.PUBLICA).all()


def get_plantillas_del_usuario(db: Session, user_id: int):
    return db.query(Plantilla).filter(Plantilla.id_usuario == user_id).all()


def update_plantilla(db: Session, plantilla_id: int, data: PlantillaUpdate):
    obj = get_plantilla(db, plantilla_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)

    db.commit()
    db.refresh(obj)
    return obj


def delete_plantilla(db: Session, plantilla_id: int):
    obj = get_plantilla(db, plantilla_id)
    db.delete(obj)
    db.commit()


def es_propietario(db: Session, plantilla_id: int, user_id: int) -> bool:
    obj = get_plantilla(db, plantilla_id)
    return obj and obj.id_usuario == user_id