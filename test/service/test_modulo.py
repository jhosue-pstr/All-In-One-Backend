import pytest
from app.models.auditoria import Auditoria
from app.models.modulo import Modulo
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

    assert result is not None
    assert result.activo is False


def test_create_modulo_duplicate_error(db):
    from app.models.modulo import Modulo
    from sqlalchemy.exc import IntegrityError

    db.add(Modulo(nombre="Test", slug="dup-test", tipo="x"))
    db.commit()

    with pytest.raises(IntegrityError):
        create_modulo(db, ModuloCreate(nombre="Test2", slug="dup-test", tipo="x"))


def test_auditoria_registra_cambios_al_actualizar_modulo(db, user):
    """
    Verifica que al modificar un módulo del sistema quede registrado en la auditoría.
    """
    modulo_test = Modulo(
        nombre="Modulo Viejo",
        slug="modulo-viejo-test",
        tipo="content",
        descripcion="Descripcion vieja",
        activo=True
    )
    db.add(modulo_test)
    db.commit()
    db.refresh(modulo_test)

    nuevos_datos = ModuloUpdate(nombre="Modulo Actualizado")

    modulo_actualizado = update_modulo(
        db=db,
        modulo_id=modulo_test.id,
        data=nuevos_datos,
        user_id=user.id
    )

    assert modulo_actualizado.nombre == "Modulo Actualizado"

    log = db.query(Auditoria).filter(
        Auditoria.entidad == "modulos",
        Auditoria.entidad_id == modulo_test.id,
        Auditoria.accion == "UPDATE"
    ).first()

    assert log is not None
    assert log.usuario_id == user.id
    assert log.valores_anteriores["nombre"] == "Modulo Viejo"
    assert log.valores_nuevos["nombre"] == "Modulo Actualizado"