from sqlalchemy.orm import Session
from app.models.sitio import Sitio
from app.schemas.sitio import SitioCreate, SitioUpdate


def create_sitio(db: Session, data: SitioCreate):
    obj = Sitio(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_sitio(db: Session, sitio_id: int):
    return db.query(Sitio).filter(Sitio.id == sitio_id).first()


def get_sitios(db: Session):
    return db.query(Sitio).all()


def update_sitio(db: Session, sitio_id: int, data: SitioUpdate):
    obj = get_sitio(db, sitio_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)

    db.commit()
    db.refresh(obj)
    return obj


def delete_sitio(db: Session, sitio_id: int):
    obj = get_sitio(db, sitio_id)
    db.delete(obj)
    db.commit()