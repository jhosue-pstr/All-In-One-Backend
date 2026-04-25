from sqlalchemy.orm import Session
from app.models.sitio import Sitio
from app.schemas.sitio import SitioCreate, SitioUpdate


def create_sitio(db: Session, data: SitioCreate, usuario_id: int = None):
    data_dict = data.model_dump()
    
    if data_dict.get('id_plantilla'):
        from app.models.plantilla import Plantilla
        plantilla = db.query(Plantilla).filter(Plantilla.id == data_dict['id_plantilla']).first()
        if plantilla and plantilla.configuracion:
            data_dict['configuracion'] = plantilla.configuracion
        if plantilla and hasattr(plantilla, 'switches') and plantilla.switches:
            data_dict['switches'] = plantilla.switches
    
    obj = Sitio(**data_dict)
    if usuario_id:
        obj.id_usuario = usuario_id
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_sitio(db: Session, sitio_id: int) -> Sitio | None:
    return (
        db.query(Sitio)
        .filter(Sitio.id == sitio_id)
        .first()
    )

def get_sitio_por_slug(db: Session, slug: str):
    return db.query(Sitio).filter(Sitio.slug == slug).first()


def get_sitios(db: Session):
    return db.query(Sitio).all()


def get_sitios_del_usuario(db: Session, usuario_id: int):
    return db.query(Sitio).filter(Sitio.id_usuario == usuario_id).all()


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