from app.schemas.sitio import SitioCreate, SitioUpdate
from app.service.sitio import (
    create_sitio,
    get_sitio,
    get_sitio_por_slug,
    get_sitios,
    get_sitios_del_usuario,
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


def test_get_sitios_del_usuario(db):
    from app.models.usuario import User
    from app.models.sitio import Sitio

    user1 = User(correo="user1@test.com", contrasena="hash", nombre="User1", apellido="Test")
    user2 = User(correo="user2@test.com", contrasena="hash", nombre="User2", apellido="Test")
    db.add_all([user1, user2])
    db.commit()
    db.refresh(user1)
    db.refresh(user2)

    db.add_all([
        Sitio(nombre="Sitio User1 A", slug="user1-a", id_usuario=user1.id),
        Sitio(nombre="Sitio User1 B", slug="user1-b", id_usuario=user1.id),
        Sitio(nombre="Sitio User2", slug="user2-a", id_usuario=user2.id),
    ])
    db.commit()

    result = get_sitios_del_usuario(db, user1.id)

    assert len(result) == 2
    assert all(s.id_usuario == user1.id for s in result)


def test_get_sitios_del_usuario_vacio(db):
    from app.models.usuario import User

    user = User(correo="empty@test.com", contrasena="hash", nombre="Empty", apellido="Test")
    db.add(user)
    db.commit()
    db.refresh(user)

    result = get_sitios_del_usuario(db, user.id)

    assert result == []


def test_get_sitio_por_slug(db):
    from app.models.sitio import Sitio

    obj = Sitio(nombre="Mi Sitio Pro", slug="mi-sitio-pro")
    db.add(obj)
    db.commit()
    db.refresh(obj)

    result = get_sitio_por_slug(db, "mi-sitio-pro")

    assert result is not None
    assert result.nombre == "Mi Sitio Pro"
    assert result.slug == "mi-sitio-pro"


def test_get_sitio_por_slug_no_existe(db):
    result = get_sitio_por_slug(db, "no-existe-12345")
    assert result is None