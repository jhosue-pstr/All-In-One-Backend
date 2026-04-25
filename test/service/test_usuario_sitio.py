import pytest
from app.packages.modulos.SiteAuth.services import usuario_sitio as services
from app.packages.modulos.SiteAuth.models.sitio_usuario import UsuarioSitio
from app.packages.modulos.SiteAuth.schemas.sitio_usuario import (
    UsuarioSitioCreate,
    UsuarioSitioUpdate,
)


def test_verify_password(db):
    hashed = services.get_password_hash("testpassword")
    assert services.verify_password("testpassword", hashed) is True
    assert services.verify_password("wrongpassword", hashed) is False


def test_get_password_hash(db):
    hashed = services.get_password_hash("password123")
    assert hashed != "password123"
    assert len(hashed) > 0


def test_create_usuario_sitio(db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Service Test Site", slug="service-test-site")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    user_data = UsuarioSitioCreate(
        correo="service@example.com",
        contrasena="password123",
        nombre="Service",
        apellido="Test",
        id_sitio=sitio.id
    )

    usuario = services.create_usuario_sitio(db, user_data)

    assert usuario is not None
    assert usuario.correo == "service@example.com"
    assert usuario.nombre == "Service"
    assert usuario.contrasena != "password123"


def test_create_usuario_sitio_correo_existente(db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Service Test Site 2", slug="service-test-site-2")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    user_data = UsuarioSitioCreate(
        correo="duplicate@example.com",
        contrasena="password123",
        nombre="Service",
        apellido="Test",
        id_sitio=sitio.id
    )

    services.create_usuario_sitio(db, user_data)
    result = services.create_usuario_sitio(db, user_data)

    assert result is None


def test_authenticate_usuario_sitio(db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Service Test Site 3", slug="service-test-site-3")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    user_data = UsuarioSitioCreate(
        correo="auth@example.com",
        contrasena="password123",
        nombre="Auth",
        apellido="Test",
        id_sitio=sitio.id
    )

    services.create_usuario_sitio(db, user_data)

    usuario = services.authenticate_usuario_sitio(
        db, "auth@example.com", "password123", sitio.id
    )

    assert usuario is not None
    assert usuario.correo == "auth@example.com"


def test_authenticate_usuario_sitio_wrong_password(db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Service Test Site 4", slug="service-test-site-4")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    user_data = UsuarioSitioCreate(
        correo="wrongpass@example.com",
        contrasena="password123",
        nombre="Wrong",
        apellido="Pass",
        id_sitio=sitio.id
    )

    services.create_usuario_sitio(db, user_data)

    usuario = services.authenticate_usuario_sitio(
        db, "wrongpass@example.com", "wrongpassword", sitio.id
    )

    assert usuario is None


def test_authenticate_usuario_sitio_no_existe(db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Service Test Site 5", slug="service-test-site-5")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    usuario = services.authenticate_usuario_sitio(
        db, "nonexistent@example.com", "password123", sitio.id
    )

    assert usuario is None


def test_update_usuario_sitio(db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Service Test Site 6", slug="service-test-site-6")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    user_data = UsuarioSitioCreate(
        correo="update@example.com",
        contrasena="password123",
        nombre="Update",
        apellido="Test",
        id_sitio=sitio.id
    )

    usuario = services.create_usuario_sitio(db, user_data)

    update_data = UsuarioSitioUpdate(nombre="Updated", apellido="Name")

    updated = services.update_usuario_sitio(db, usuario, update_data)

    assert updated.nombre == "Updated"
    assert updated.apellido == "Name"


def test_update_usuario_sitio_password(db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Service Test Site 7", slug="service-test-site-7")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    user_data = UsuarioSitioCreate(
        correo="updatepass@example.com",
        contrasena="password123",
        nombre="Update",
        apellido="Pass",
        id_sitio=sitio.id
    )

    usuario = services.create_usuario_sitio(db, user_data)

    update_data = UsuarioSitioUpdate(contrasena="newpassword123")

    updated = services.update_usuario_sitio(db, usuario, update_data)

    assert updated.contrasena != "newpassword123"
    assert services.verify_password("newpassword123", updated.contrasena)


def test_login_usuario_sitio(db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Service Test Site 8", slug="service-test-site-8")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    user_data = UsuarioSitioCreate(
        correo="login@example.com",
        contrasena="password123",
        nombre="Login",
        apellido="Test",
        id_sitio=sitio.id
    )

    usuario = services.create_usuario_sitio(db, user_data)
    token = services.login_usuario_sitio(db, usuario)

    assert token is not None
    assert len(token) > 0

    db.refresh(usuario)
    assert usuario.token == token


def test_logout_usuario_sitio(db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Service Test Site 9", slug="service-test-site-9")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    user_data = UsuarioSitioCreate(
        correo="logout@example.com",
        contrasena="password123",
        nombre="Logout",
        apellido="Test",
        id_sitio=sitio.id
    )

    usuario = services.create_usuario_sitio(db, user_data)
    services.login_usuario_sitio(db, usuario)

    result = services.logout_usuario_sitio(db, usuario)

    assert result is True

    db.refresh(usuario)
    assert usuario.token is None


def test_verify_token_usuario_sitio(db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Service Test Site 10", slug="service-test-site-10")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    user_data = UsuarioSitioCreate(
        correo="verify@example.com",
        contrasena="password123",
        nombre="Verify",
        apellido="Test",
        id_sitio=sitio.id
    )

    usuario = services.create_usuario_sitio(db, user_data)
    token = services.login_usuario_sitio(db, usuario)

    verified = services.verify_token_usuario_sitio(db, token)

    assert verified is not None
    assert verified.id == usuario.id


def test_verify_token_usuario_sitio_invalido(db):
    verified = services.verify_token_usuario_sitio(db, "invalid_token")
    assert verified is None


def test_verify_token_usuario_sitio_after_logout(db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Service Test Site 11", slug="service-test-site-11")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    user_data = UsuarioSitioCreate(
        correo="verifylogout@example.com",
        contrasena="password123",
        nombre="Verify",
        apellido="Logout",
        id_sitio=sitio.id
    )

    usuario = services.create_usuario_sitio(db, user_data)
    token = services.login_usuario_sitio(db, usuario)
    services.logout_usuario_sitio(db, usuario)

    verified = services.verify_token_usuario_sitio(db, token)

    assert verified is None


def test_get_usuario_by_id(db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Service Test Site 12", slug="service-test-site-12")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    user_data = UsuarioSitioCreate(
        correo="getbyid@example.com",
        contrasena="password123",
        nombre="Get",
        apellido="ById",
        id_sitio=sitio.id
    )

    usuario = services.create_usuario_sitio(db, user_data)

    found = services.get_usuario_by_id(db, usuario.id)

    assert found is not None
    assert found.id == usuario.id


def test_get_usuario_by_id_no_existe(db):
    found = services.get_usuario_by_id(db, 99999)
    assert found is None


def test_create_access_token(db):
    token = services.create_access_token(data={"sub": "123", "test": "data"})
    assert token is not None
    assert len(token) > 0