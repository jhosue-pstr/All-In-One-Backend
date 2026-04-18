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


def test_create_modulo(client, user_data):
    headers = get_auth_header(client, user_data)
    response = client.post(
        "/api/modulos",
        json={"nombre": "Blog", "slug": "blog", "descripcion": "Blog description", "tipo": "content"},
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Blog"
    assert data["slug"] == "blog"


def test_get_modulo(client, user_data):
    headers = get_auth_header(client, user_data)
    create_response = client.post(
        "/api/modulos",
        json={"nombre": "Test", "slug": "test-mod", "descripcion": "Test", "tipo": "content"},
        headers=headers
    )
    modulo_id = create_response.json()["id"]

    response = client.get(f"/api/modulos/{modulo_id}")

    assert response.status_code == 200
    assert response.json()["id"] == modulo_id


def test_get_modulos(client, user_data):
    headers = get_auth_header(client, user_data)
    client.post("/api/modulos", json={"nombre": "A", "slug": "mod-a", "tipo": "content"}, headers=headers)
    client.post("/api/modulos", json={"nombre": "B", "slug": "mod-b", "tipo": "content"}, headers=headers)

    response = client.get("/api/modulos")

    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_update_modulo(client, user_data):
    headers = get_auth_header(client, user_data)
    create_response = client.post(
        "/api/modulos",
        json={"nombre": "Old", "slug": "old-mod", "tipo": "content"},
        headers=headers
    )
    modulo_id = create_response.json()["id"]

    response = client.put(
        f"/api/modulos/{modulo_id}",
        json={"nombre": "New"},
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["nombre"] == "New"


def test_delete_modulo(client, user_data):
    headers = get_auth_header(client, user_data)
    create_response = client.post(
        "/api/modulos",
        json={"nombre": "Delete", "slug": "delete-mod", "tipo": "content"},
        headers=headers
    )
    modulo_id = create_response.json()["id"]

    response = client.delete(f"/api/modulos/{modulo_id}", headers=headers)

    assert response.status_code == 204

    get_response = client.get(f"/api/modulos/{modulo_id}")
    assert get_response.status_code == 404


def test_get_modulo_not_found(client):
    response = client.get("/api/modulos/9999")
    assert response.status_code == 404


def test_update_modulo_not_found(client, user_data):
    headers = get_auth_header(client, user_data)
    response = client.put("/api/modulos/9999", json={"nombre": "New"}, headers=headers)
    assert response.status_code == 404


def test_delete_modulo_not_found(client, user_data):
    headers = get_auth_header(client, user_data)
    response = client.delete("/api/modulos/9999", headers=headers)
    assert response.status_code == 404