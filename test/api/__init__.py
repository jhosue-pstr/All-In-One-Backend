from app.schemas.sitio import SitioCreate, SitioUpdate
from app.service.sitio import (
    create_sitio,
    get_sitio,
    get_sitios,
    update_sitio,
    delete_sitio,
)


def test_create_sitio(db):
    data = SitioCreate(
        nombre="Mi sitio",
        slug="mi-sitio"
    )

    sitio = create_sitio(db, data)

    assert sitio.id is not None
    assert sitio.nombre == "Mi sitio"
    assert sitio.slug == "mi-sitio"


def test_get_sitio(db):
    from app.models.sitio import Sitio

    obj = Sitio(nombre="Test", slug="test")
    db.add(obj)
    db.commit()
    db.refresh(obj)

    result = get_sitio(db, obj.id)

    assert result is not None
    assert result.id == obj.id


def test_get_sitios(db):
    from app.models.sitio import Sitio

    db.add_all([
        Sitio(nombre="A", slug="a"),
        Sitio(nombre="B", slug="b"),
    ])
    db.commit()

    result = get_sitios(db)

    assert len(result) >= 2


def test_update_sitio(db):
    from app.models.sitio import Sitio

    obj = Sitio(nombre="Viejo", slug="viejo")
    db.add(obj)
    db.commit()
    db.refresh(obj)

    update_data = SitioUpdate(nombre="Nuevo")

    updated = update_sitio(db, obj.id, update_data)

    assert updated.nombre == "Nuevo"


def test_delete_sitio(db):
    from app.models.sitio import Sitio

    obj = Sitio(nombre="Eliminar", slug="eliminar")
    db.add(obj)
    db.commit()
    db.refresh(obj)

    delete_sitio(db, obj.id)

    result = db.query(Sitio).filter(Sitio.id == obj.id).first()

    assert result is None