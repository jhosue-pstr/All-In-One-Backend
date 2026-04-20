import pytest


def get_auth_header(client, user_data):
    client.post("/api/auth/registro", json=user_data)
    login_response = client.post(
        "/api/auth/inicio",
        data={
            "username": user_data["correo"],
            "password": user_data["contrasena"]
        }
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_sitio(client, user_data):
    headers = get_auth_header(client, user_data)
    response = client.post(
        "/api/sitios",
        json={"nombre": "Sitio Test", "slug": "sitio-test"},
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Sitio Test"
    assert data["slug"] == "sitio-test"


def test_get_sitio(client, user_data):
    headers = get_auth_header(client, user_data)
    create_response = client.post(
        "/api/sitios",
        json={"nombre": "Test", "slug": "test-sitio"},
        headers=headers
    )
    sitio_id = create_response.json()["id"]

    response = client.get(f"/api/sitios/{sitio_id}")

    assert response.status_code == 200
    assert response.json()["id"] == sitio_id


def test_get_sitios(client, user_data):
    headers = get_auth_header(client, user_data)
    client.post("/api/sitios", json={"nombre": "A", "slug": "sitio-a"}, headers=headers)
    client.post("/api/sitios", json={"nombre": "B", "slug": "sitio-b"}, headers=headers)

    response = client.get("/api/sitios")

    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_update_sitio(client, user_data):
    headers = get_auth_header(client, user_data)
    create_response = client.post(
        "/api/sitios",
        json={"nombre": "Old", "slug": "old-sitio"},
        headers=headers
    )
    sitio_id = create_response.json()["id"]

    response = client.put(
        f"/api/sitios/{sitio_id}",
        json={"nombre": "New"},
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["nombre"] == "New"


def test_delete_sitio(client, user_data):
    headers = get_auth_header(client, user_data)
    create_response = client.post(
        "/api/sitios",
        json={"nombre": "Delete", "slug": "delete-sitio"},
        headers=headers
    )
    sitio_id = create_response.json()["id"]

    response = client.delete(f"/api/sitios/{sitio_id}", headers=headers)

    assert response.status_code == 204

    get_response = client.get(f"/api/sitios/{sitio_id}")
    assert get_response.status_code == 404


def test_get_sitio_not_found(client):
    response = client.get("/api/sitios/9999")
    assert response.status_code == 404


def test_update_sitio_not_found(client, user_data):
    headers = get_auth_header(client, user_data)
    response = client.put("/api/sitios/9999", json={"nombre": "New"}, headers=headers)
    assert response.status_code == 404


def test_delete_sitio_not_found(client, user_data):
    headers = get_auth_header(client, user_data)
    response = client.delete("/api/sitios/9999", headers=headers)
    assert response.status_code == 404


def test_mis_sitios(client, user_data):
    headers = get_auth_header(client, user_data)
    client.post("/api/sitios", json={"nombre": "Mi Sitio", "slug": "mi-sitio"}, headers=headers)
    client.post("/api/sitios", json={"nombre": "Otro", "slug": "otro-sitio"}, headers=headers)

    response = client.get("/api/sitios/mis-sitios", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["nombre"] == "Mi Sitio"


def test_mis_sitios_vacio(client, user_data):
    headers = get_auth_header(client, user_data)

    response = client.get("/api/sitios/mis-sitios", headers=headers)

    assert response.status_code == 200
    assert response.json() == []


def test_mis_sitios_sin_auth(client):
    response = client.get("/api/sitios/mis-sitios")
    assert response.status_code == 401


def test_upload_miniatura(client, user_data):
    from io import BytesIO
    
    headers = get_auth_header(client, user_data)
    create_response = client.post(
        "/api/sitios",
        json={"nombre": "Con Miniatura", "slug": "con-miniatura"},
        headers=headers
    )
    sitio_id = create_response.json()["id"]

    file_content = BytesIO(b"fake image content")
    file_content.name = "test.png"
    
    response = client.post(
        f"/api/sitios/{sitio_id}/miniatura",
        files={"file": ("test.png", b"fake image content", "image/png")},
        headers=headers
    )

    assert response.status_code == 200
    assert "url" in response.json()


def test_upload_miniatura_no_propietario(client, user_data):
    from app.models.usuario import User
    
    headers = get_auth_header(client, user_data)
    
    client.post("/api/auth/registro", json={
        "correo": "otro@test.com",
        "contrasena": "123456",
        "nombre": "Otro",
        "apellido": "Usuario"
    })
    login_response = client.post(
        "/api/auth/inicio",
        data={
            "username": "otro@test.com",
            "password": "123456"
        }
    )
    otro_token = login_response.json()["access_token"]
    otro_headers = {"Authorization": f"Bearer {otro_token}"}
    
    create_response = client.post(
        "/api/sitios",
        json={"nombre": "Sitio Owner", "slug": "sitio-owner"},
        headers=headers
    )
    sitio_id = create_response.json()["id"]

    response = client.post(
        f"/api/sitios/{sitio_id}/miniatura",
        files={"file": ("test.png", b"fake", "image/png")},
        headers=otro_headers
    )

    assert response.status_code == 403