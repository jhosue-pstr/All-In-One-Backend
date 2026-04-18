from sqlalchemy.orm import Session
from app.models.modulo import Modulo
from app.schemas.modulo import ModuloCreate, ModuloUpdate


def create_modulo(db: Session, data: ModuloCreate):
    obj = Modulo(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_modulo(db: Session, modulo_id: int):
    return db.query(Modulo).filter(Modulo.id == modulo_id).first()


def get_modulos(db: Session):
    return db.query(Modulo).all()


def update_modulo(db: Session, modulo_id: int, data: ModuloUpdate):
    obj = get_modulo(db, modulo_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)

    db.commit()
    db.refresh(obj)
    return obj


def delete_modulo(db: Session, modulo_id: int):
    obj = get_modulo(db, modulo_id)
    db.delete(obj)
    db.commit()