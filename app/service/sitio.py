from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.models.sitio import Sitio
from app.models.auditoria import Auditoria  # <- Importación del modelo de auditoría
from app.schemas.sitio import SitioCreate, SitioUpdate


def create_sitio(db: Session, data: SitioCreate, usuario_id: int = None):
    data_dict = data.model_dump()
    
    if data_dict.get('id_plantilla'):
        from app.models.plantilla import Plantilla
        plantilla = db.query(Plantilla).filter(Plantilla.id == data_dict['id_plantilla'], Plantilla.activo == True).first()
        if plantilla and plantilla.configuracion:
            data_dict['configuracion'] = plantilla.configuracion
        if plantilla and hasattr(plantilla, 'switches') and plantilla.switches:
            data_dict['switches'] = plantilla.switches
    
    obj = Sitio(**data_dict)
    if usuario_id:
        obj.id_usuario = usuario_id
        
    db.add(obj)
    # Hacemos flush para que PostgreSQL genere el obj.id sin cerrar la transacción
    db.flush() 
    
    # --- INICIO AUDITORÍA (INSERT) ---
    valores_nuevos = jsonable_encoder(obj)
    auditoria = Auditoria(
        entidad="sitios",
        entidad_id=obj.id,
        accion="INSERT",
        usuario_id=usuario_id,
        valores_anteriores=None,
        valores_nuevos=valores_nuevos
    )
    db.add(auditoria)
    # --- FIN AUDITORÍA ---

    db.commit()
    db.refresh(obj)
    return obj


def get_sitio(db: Session, sitio_id: int) -> Sitio | None:
    # FILTRO SOFT DELETE: Solo traer si activo es True
    return (
        db.query(Sitio)
        .filter(Sitio.id == sitio_id, Sitio.activo == True)
        .first()
    )


def get_sitio_por_slug(db: Session, slug: str):
    # FILTRO SOFT DELETE: Solo traer si activo es True
    return db.query(Sitio).filter(Sitio.slug == slug, Sitio.activo == True).first()


def get_sitios(db: Session):
    # FILTRO SOFT DELETE: Solo traer si activo es True
    return db.query(Sitio).filter(Sitio.activo == True).all()


def get_sitios_del_usuario(db: Session, usuario_id: int):
    # FILTRO SOFT DELETE: Solo traer si activo es True
    return db.query(Sitio).filter(Sitio.id_usuario == usuario_id, Sitio.activo == True).all()


def update_sitio(db: Session, sitio_id: int, data: SitioUpdate, usuario_id: int = None):
    obj = get_sitio(db, sitio_id)
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
        entidad="sitios",
        entidad_id=obj.id,
        accion="UPDATE",
        usuario_id=usuario_id,
        valores_anteriores=valores_anteriores,
        valores_nuevos=valores_nuevos
    )
    db.add(auditoria)
    # --- FIN AUDITORÍA ---

    db.commit()
    db.refresh(obj)
    return obj


def delete_sitio(db: Session, sitio_id: int, usuario_id: int = None):
    obj = get_sitio(db, sitio_id)
    if not obj:
        return None

    # --- INICIO AUDITORÍA (DELETE) ---
    valores_anteriores = jsonable_encoder(obj)
    auditoria = Auditoria(
        entidad="sitios",
        entidad_id=obj.id,
        accion="DELETE",
        usuario_id=usuario_id,
        valores_anteriores=valores_anteriores,
        valores_nuevos=None
    )
    db.add(auditoria)
    # --- FIN AUDITORÍA ---

    # TRUCO SOFT DELETE: Cambiamos el estado en vez de db.delete()
    obj.activo = False
    db.commit()
    return obj