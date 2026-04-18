from app.schemas.plantilla import PlantillaCreate, PlantillaUpdate
from app.service.plantilla import (
    create_plantilla,
    get_plantillas,
    get_plantilla,
    update_plantilla,
    delete_plantilla,
)


def test_crear_plantilla(db):
    data = PlantillaCreate(
        nombre="Plantilla 1",
        slug="plantilla-1"
    )

    plantilla = create_plantilla(db, data)

    assert plantilla.id is not None
    assert plantilla.nombre == "Plantilla 1"
    assert plantilla.slug == "plantilla-1"


def test_obtener_plantilla(db):
    from app.models.plantilla import Plantilla

    obj = Plantilla(nombre="Test", slug="test")
    db.add(obj)
    db.commit()
    db.refresh(obj)

    result = get_plantilla(db, obj.id)

    assert result is not None
    assert result.id == obj.id    


def test_obtener_plantillas(db):
    from app.models.plantilla import Plantilla

    db.add_all([
        Plantilla(nombre="A", slug="a"),
        Plantilla(nombre="B", slug="b"),
    ])
    db.commit()

    result = get_plantillas(db)

    assert len(result) >= 2


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