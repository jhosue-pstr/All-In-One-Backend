from app.schemas.plantilla import PlantillaCreate, PlantillaUpdate
from app.service.plantilla import (
    create_plantilla,
    get_plantillas,
    get_plantilla,
    get_plantillas_publicas,
    get_plantillas_del_usuario,
    update_plantilla,
    delete_plantilla,
    es_propietario,
)
from app.models.plantilla import Plantilla, Visibilidad


def test_crear_plantilla_asigna_usuario(db, user):
    data = PlantillaCreate(nombre="Plantilla 1", slug="plantilla-1")

    plantilla = create_plantilla(db, data, user.id)

    assert plantilla.id is not None
    assert plantilla.nombre == "Plantilla 1"
    assert plantilla.slug == "plantilla-1"
    assert plantilla.id_usuario == user.id
    assert plantilla.visibilidad == Visibilidad.PRIVADA


def test_crear_plantilla_publica(db, user):
    data = PlantillaCreate(nombre="Publica", slug="publica", visibilidad=Visibilidad.PUBLICA)

    plantilla = create_plantilla(db, data, user.id)

    assert plantilla.visibilidad == Visibilidad.PUBLICA


def test_obtener_plantilla(db):
    from app.models.plantilla import Plantilla

    obj = Plantilla(nombre="Test", slug="test", visibilidad=Visibilidad.PUBLICA)
    db.add(obj)
    db.commit()
    db.refresh(obj)

    result = get_plantilla(db, obj.id)

    assert result is not None
    assert result.id == obj.id


def test_obtener_plantillas_publicas(db, user):
    db.add_all([
        Plantilla(nombre="Publica", slug="publica-a", visibilidad=Visibilidad.PUBLICA),
        Plantilla(nombre="Privada", slug="privada-a", visibilidad=Visibilidad.PRIVADA, id_usuario=user.id),
    ])
    db.commit()

    result = get_plantillas_publicas(db)

    assert all(p.visibilidad == Visibilidad.PUBLICA for p in result)


def test_obtener_plantillas_del_usuario(db, user):
    db.add_all([
        Plantilla(nombre="Mi Plantilla", slug="mi-plantilla-a", id_usuario=user.id),
        Plantilla(nombre="Otra", slug="otra-a", visibilidad=Visibilidad.PUBLICA),
    ])
    db.commit()

    result = get_plantillas_del_usuario(db, user.id)

    assert len(result) >= 1


def test_actualizar_plantilla(db):
    from app.models.plantilla import Plantilla

    obj = Plantilla(nombre="Old", slug="old")
    db.add(obj)
    db.commit()
    db.refresh(obj)

    update_data = PlantillaUpdate(nombre="New")

    updated = update_plantilla(db, obj.id, update_data)

    assert updated.nombre == "New"


def test_eliminar_plantilla(db):
    from app.models.plantilla import Plantilla

    obj = Plantilla(nombre="Delete", slug="delete")
    db.add(obj)
    db.commit()
    db.refresh(obj)

    delete_plantilla(db, obj.id)

    result = db.query(Plantilla).filter(Plantilla.id == obj.id).first()

    assert result is None