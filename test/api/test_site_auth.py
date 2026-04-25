import pytest
from app.packages.modulos.SiteAuth.models.sitio_usuario import UsuarioSitio


def test_registro_success(client, db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Test Site", slug="test-site")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    user_data = {
        "correo": "user@example.com",
        "contrasena": "password123",
        "nombre": "Test",
        "apellido": "User",
        "id_sitio": sitio.id
    }

    response = client.post("/api/site-auth/registro", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["correo"] == user_data["correo"]
    assert data["nombre"] == user_data["nombre"]
    assert data["id_sitio"] == sitio.id


def test_registro_correo_existente(client, db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Test Site 2", slug="test-site-2")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    user_data = {
        "correo": "existing@example.com",
        "contrasena": "password123",
        "nombre": "Test",
        "apellido": "User",
        "id_sitio": sitio.id
    }

    client.post("/api/site-auth/registro", json=user_data)

    response = client.post("/api/site-auth/registro", json=user_data)
    assert response.status_code == 400
    assert "ya esta registrado" in response.text


def test_login_success(client, db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Test Site 3", slug="test-site-3")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    user_data = {
        "correo": "login@example.com",
        "contrasena": "password123",
        "nombre": "Test",
        "apellido": "User",
        "id_sitio": sitio.id
    }

    client.post("/api/site-auth/registro", json=user_data)

    response = client.post("/api/site-auth/login", json={
        "correo": "login@example.com",
        "contrasena": "password123",
        "id_sitio": sitio.id
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_contrasena_incorrecta(client, db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Test Site 4", slug="test-site-4")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    user_data = {
        "correo": "wrongpass@example.com",
        "contrasena": "password123",
        "nombre": "Test",
        "apellido": "User",
        "id_sitio": sitio.id
    }

    client.post("/api/site-auth/registro", json=user_data)

    response = client.post("/api/site-auth/login", json={
        "correo": "wrongpass@example.com",
        "contrasena": "wrongpassword",
        "id_sitio": sitio.id
    })

    assert response.status_code == 401
    assert "Credenciales incorrectas" in response.text


def test_login_usuario_no_existe(client, db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Test Site 5", slug="test-site-5")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    response = client.post("/api/site-auth/login", json={
        "correo": "nonexistent@example.com",
        "contrasena": "password123",
        "id_sitio": sitio.id
    })

    assert response.status_code == 401


def test_me_success(client, db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Test Site 6", slug="test-site-6")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    user_data = {
        "correo": "me@example.com",
        "contrasena": "password123",
        "nombre": "Test",
        "apellido": "User",
        "id_sitio": sitio.id
    }

    client.post("/api/site-auth/registro", json=user_data)

    login_response = client.post("/api/site-auth/login", json={
        "correo": "me@example.com",
        "contrasena": "password123",
        "id_sitio": sitio.id
    })

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/site-auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["correo"] == "me@example.com"
    assert data["nombre"] == "Test"


def test_me_sin_token(client):
    response = client.get("/api/site-auth/me")
    assert response.status_code == 401


def test_me_token_invalido(client):
    response = client.get(
        "/api/site-auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


def test_update_me_success(client, db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Test Site 7", slug="test-site-7")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    user_data = {
        "correo": "update@example.com",
        "contrasena": "password123",
        "nombre": "Test",
        "apellido": "User",
        "id_sitio": sitio.id
    }

    client.post("/api/site-auth/registro", json=user_data)

    login_response = client.post("/api/site-auth/login", json={
        "correo": "update@example.com",
        "contrasena": "password123",
        "id_sitio": sitio.id
    })

    token = login_response.json()["access_token"]

    response = client.put(
        "/api/site-auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"nombre": "Updated", "apellido": "Name"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Updated"
    assert data["apellido"] == "Name"


def test_update_me_password(client, db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Test Site 8", slug="test-site-8")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    user_data = {
        "correo": "updatepass@example.com",
        "contrasena": "password123",
        "nombre": "Test",
        "apellido": "User",
        "id_sitio": sitio.id
    }

    client.post("/api/site-auth/registro", json=user_data)

    login_response = client.post("/api/site-auth/login", json={
        "correo": "updatepass@example.com",
        "contrasena": "password123",
        "id_sitio": sitio.id
    })

    token = login_response.json()["access_token"]

    client.put(
        "/api/site-auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"contrasena": "newpassword123"}
    )

    login_response = client.post("/api/site-auth/login", json={
        "correo": "updatepass@example.com",
        "contrasena": "newpassword123",
        "id_sitio": sitio.id
    })

    assert login_response.status_code == 200


def test_verify_token_success(client, db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Test Site 9", slug="test-site-9")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    user_data = {
        "correo": "verify@example.com",
        "contrasena": "password123",
        "nombre": "Test",
        "apellido": "User",
        "id_sitio": sitio.id
    }

    client.post("/api/site-auth/registro", json=user_data)

    login_response = client.post("/api/site-auth/login", json={
        "correo": "verify@example.com",
        "contrasena": "password123",
        "id_sitio": sitio.id
    })

    token = login_response.json()["access_token"]

    response = client.get(f"/api/site-auth/verify?token={token}")

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert "usuario_id" in data


def test_verify_token_invalido(client):
    response = client.get("/api/site-auth/verify?token=invalid_token")
    assert response.status_code == 401


def test_logout_success(client, db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Test Site 10", slug="test-site-10")
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    user_data = {
        "correo": "logout@example.com",
        "contrasena": "password123",
        "nombre": "Test",
        "apellido": "User",
        "id_sitio": sitio.id
    }

    client.post("/api/site-auth/registro", json=user_data)

    login_response = client.post("/api/site-auth/login", json={
        "correo": "logout@example.com",
        "contrasena": "password123",
        "id_sitio": sitio.id
    })

    token = login_response.json()["access_token"]

    response = client.post(
        "/api/site-auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert "Logout exitoso" in response.json()["message"]

    response = client.get(
        "/api/site-auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


def test_logout_sin_token(client):
    response = client.post("/api/site-auth/logout")
    assert response.status_code == 401