from app.models.auditoria import Auditoria
from app.models.sitio import Sitio
from app.models.modulo import Modulo
from app.service.sitio_modulo import agregar_modulo_a_sitio
import pytest
from app.service.sitio_modulo import (
    agregar_modulo_a_sitio,
    quitar_modulo_de_sitio,
    get_modulos_del_sitio,
)


def test_agregar_modulo_a_sitio(db):
    from app.models.sitio import Sitio
    from app.models.modulo import Modulo

    sitio = Sitio(nombre="Sitio Test", slug="sitio-test")
    modulo = Modulo(nombre="Blog", slug="blog", tipo="content")
    db.add(sitio)
    db.add(modulo)
    db.commit()
    db.refresh(sitio)
    db.refresh(modulo)

    result = agregar_modulo_a_sitio(db, sitio.id, modulo.id)

    assert result is not None
    assert modulo in result.modulos


def test_agregar_modulo_inexistente(db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Sitio Test", slug="sitio-test2")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    result = agregar_modulo_a_sitio(db, sitio.id, 9999)

    assert result is None


def test_agregar_modulo_sitio_inexistente(db):
    result = agregar_modulo_a_sitio(db, 9999, 1)
    assert result is None


def test_quitar_modulo_de_sitio_inexistente(db):
    result = quitar_modulo_de_sitio(db, 9999, 1)
    assert result is None


def test_quitar_modulo_de_sitio(db):
    from app.models.sitio import Sitio
    from app.models.modulo import Modulo

    sitio = Sitio(nombre="Sitio Test", slug="sitio-test3")
    modulo = Modulo(nombre="Blog", slug="blog-rem", tipo="content")
    db.add(sitio)
    db.add(modulo)
    db.commit()
    db.refresh(sitio)
    db.refresh(modulo)

    sitio.modulos.append(modulo)
    db.commit()

    result = quitar_modulo_de_sitio(db, sitio.id, modulo.id)

    assert result is not None
    assert modulo not in result.modulos


def test_get_modulos_del_sitio(db):
    from app.models.sitio import Sitio
    from app.models.modulo import Modulo

    sitio = Sitio(nombre="Sitio Test", slug="sitio-test4")
    modulo1 = Modulo(nombre="Blog", slug="blog-mod", tipo="content")
    modulo2 = Modulo(nombre="Tienda", slug="tienda-mod", tipo="ecommerce")
    db.add_all([sitio, modulo1, modulo2])
    db.commit()
    db.refresh(sitio)
    db.refresh(modulo1)
    db.refresh(modulo2)

    sitio.modulos.extend([modulo1, modulo2])
    db.commit()

    result = get_modulos_del_sitio(db, sitio.id)

    assert result is not None
    assert len(result) == 2


def test_get_modulos_sitio_inexistente(db):
    result = get_modulos_del_sitio(db, 9999)
    assert result is None

def test_auditoria_registra_cuando_se_agrega_modulo_a_sitio(db, user):
    """
    Verifica que al conectar un módulo a un sitio se genere una auditoría tipo INSERT.
    """
    sitio = Sitio(nombre="Sitio de Test", slug="sitio-test-rel", id_usuario=user.id)
    modulo = Modulo(nombre="Auth Module", slug="auth-mod-rel", tipo="auth", descripcion="Módulo de seguridad")
    db.add_all([sitio, modulo])
    db.commit()
    db.refresh(sitio)
    db.refresh(modulo)

    agregar_modulo_a_sitio(db=db, sitio_id=sitio.id, modulo_id=modulo.id, user_id=user.id)

    log = db.query(Auditoria).filter(
        Auditoria.entidad == "sitio_modulo",
        Auditoria.entidad_id == sitio.id,
        Auditoria.accion == "INSERT"
    ).first()

    assert log is not None
    assert log.usuario_id == user.id
    assert log.valores_nuevos["modulo_id"] == modulo.id
    # Corregimos la llave al nombre correcto:
    assert log.valores_nuevos["modulo_nombre"] == "Auth Module"

def test_quitar_modulo_inexistente_pero_sitio_existe(db):
    """
    Cubre la línea 43: El sitio existe, pero se intenta quitar un ID de módulo que no existe.
    """
    from app.models.sitio import Sitio
    from app.service.sitio_modulo import quitar_modulo_de_sitio

    sitio = Sitio(nombre="Sitio Cobertura", slug="sitio-cob")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    # 9999 es un ID de módulo que sabemos que no existe
    result = quitar_modulo_de_sitio(db, sitio.id, 9999)

    assert result is None