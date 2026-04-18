from app.schemas.sitio import SitioCreate, SitioUpdate
from app.service.sitio import (
    create_sitio,
    get_sitio,
    get_sitios,
    update_sitio,
    delete_sitio,
)


def test_create_sitio(db):
    from app.models.usuario import User
    from app.models.plantilla import Plantilla

    usuario = User(
        correo="owner@test.com",
        contrasena="hash",
        nombre="Owner",
        apellido="Test"
    )
    db.add(usuario)
    
    plantilla = Plantilla(nombre="Basic", slug="basic")
    db.add(plantilla)
    db.commit()
    db.refresh(usuario)
    db.refresh(plantilla)

    data = SitioCreate(
        nombre="Mi Sitio",
        slug="mi-sitio",
        id_usuario=usuario.id,
        id_plantilla=plantilla.id,
        switches={"blog": True, "tienda": False}
    )

    sitio = create_sitio(db, data)

    assert sitio.id is not None
    assert sitio.nombre == "Mi Sitio"
    assert sitio.slug == "mi-sitio"
    assert sitio.switches == {"blog": True, "tienda": False}


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

    update_data = SitioUpdate(nombre="Nuevo", switches={"blog": True})

    updated = update_sitio(db, obj.id, update_data)

    assert updated.nombre == "Nuevo"
    assert updated.switches == {"blog": True}


def test_delete_sitio(db):
    from app.models.sitio import Sitio

    obj = Sitio(nombre="Eliminar", slug="eliminar")
    db.add(obj)
    db.commit()
    db.refresh(obj)

    delete_sitio(db, obj.id)

    result = db.query(Sitio).filter(Sitio.id == obj.id).first()

    assert result is None


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

    from app.service.sitio_modulo import agregar_modulo_a_sitio
    result = agregar_modulo_a_sitio(db, sitio.id, modulo.id)

    assert result is not None
    assert modulo in result.modulos


def test_quitar_modulo_de_sitio(db):
    from app.models.sitio import Sitio
    from app.models.modulo import Modulo

    sitio = Sitio(nombre="Sitio Test", slug="sitio-test2")
    modulo = Modulo(nombre="Blog", slug="blog2", tipo="content")
    db.add(sitio)
    db.add(modulo)
    db.commit()
    db.refresh(sitio)
    db.refresh(modulo)

    sitio.modulos.append(modulo)
    db.commit()

    from app.service.sitio_modulo import quitar_modulo_de_sitio
    result = quitar_modulo_de_sitio(db, sitio.id, modulo.id)

    assert result is not None
    assert modulo not in result.modulos


def test_get_modulos_del_sitio(db):
    from app.models.sitio import Sitio
    from app.models.modulo import Modulo

    sitio = Sitio(nombre="Sitio Test", slug="sitio-test3")
    modulo1 = Modulo(nombre="Blog", slug="blog3", tipo="content")
    modulo2 = Modulo(nombre="Tienda", slug="tienda1", tipo="ecommerce")
    db.add_all([sitio, modulo1, modulo2])
    db.commit()
    db.refresh(sitio)
    db.refresh(modulo1)
    db.refresh(modulo2)

    sitio.modulos.extend([modulo1, modulo2])
    db.commit()

    from app.service.sitio_modulo import get_modulos_del_sitio
    result = get_modulos_del_sitio(db, sitio.id)

    assert result is not None
    assert len(result) == 2