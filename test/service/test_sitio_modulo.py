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