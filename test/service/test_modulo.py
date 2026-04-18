from app.schemas.modulo import ModuloCreate, ModuloUpdate
from app.service.modulo import (
    create_modulo,
    get_modulo,
    get_modulos,
    update_modulo,
    delete_modulo,
)


def test_create_modulo(db):
    data = ModuloCreate(
        nombre="Login",
        slug="login",
        tipo="auth"
    )

    modulo = create_modulo(db, data)

    assert modulo.id is not None
    assert modulo.nombre == "Login"
    assert modulo.slug == "login"


def test_get_modulo(db):
    from app.models.modulo import Modulo

    obj = Modulo(nombre="Test", slug="test", tipo="test")
    db.add(obj)
    db.commit()
    db.refresh(obj)

    result = get_modulo(db, obj.id)

    assert result is not None
    assert result.id == obj.id


def test_get_modulos(db):
    from app.models.modulo import Modulo

    db.add_all([
        Modulo(nombre="A", slug="a", tipo="x"),
        Modulo(nombre="B", slug="b", tipo="x"),
    ])
    db.commit()

    result = get_modulos(db)

    assert len(result) >= 2


def test_update_modulo(db):
    from app.models.modulo import Modulo

    obj = Modulo(nombre="Viejo", slug="viejo", tipo="x")
    db.add(obj)
    db.commit()
    db.refresh(obj)

    update_data = ModuloUpdate(nombre="Nuevo")

    updated = update_modulo(db, obj.id, update_data)

    assert updated.nombre == "Nuevo"


def test_delete_modulo(db):
    from app.models.modulo import Modulo

    obj = Modulo(nombre="Eliminar", slug="eliminar", tipo="x")
    db.add(obj)
    db.commit()
    db.refresh(obj)

    delete_modulo(db, obj.id)

    result = db.query(Modulo).filter(Modulo.id == obj.id).first()

    assert result is None