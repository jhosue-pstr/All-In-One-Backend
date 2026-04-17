from sqlalchemy.orm import Session
from app.models.plantilla import Plantilla
from app.schemas.plantilla import PlantillaCreate, PlantillaUpdate


def create_plantilla(db: Session, data: PlantillaCreate):
    obj = Plantilla(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_plantilla(db: Session, plantilla_id: int):
    return db.query(Plantilla).filter(Plantilla.id == plantilla_id).first()


def get_plantillas(db: Session):
    return db.query(Plantilla).all()


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