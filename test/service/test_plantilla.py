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


def test_create_plantilla(client, user_data):
    headers = get_auth_header(client, user_data)
    response = client.post(
        "/api/plantillas",
        json={"nombre": "Plantilla 1", "slug": "plantilla-1"},
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Plantilla 1"
    assert data["slug"] == "plantilla-1"


def test_get_plantilla(client, user_data):
    headers = get_auth_header(client, user_data)
    create_response = client.post(
        "/api/plantillas",
        json={"nombre": "Test", "slug": "test"},
        headers=headers
    )
    planta_id = create_response.json()["id"]

    response = client.get(f"/api/plantillas/{planta_id}")

    assert response.status_code == 200
    assert response.json()["id"] == planta_id


def test_get_plantillas(client, user_data):
    headers = get_auth_header(client, user_data)
    client.post("/api/plantillas", json={"nombre": "A", "slug": "a"}, headers=headers)
    client.post("/api/plantillas", json={"nombre": "B", "slug": "b"}, headers=headers)

    response = client.get("/api/plantillas")

    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_update_plantilla(client, user_data):
    headers = get_auth_header(client, user_data)
    create_response = client.post(
        "/api/plantillas",
        json={"nombre": "Old", "slug": "old"},
        headers=headers
    )
    planta_id = create_response.json()["id"]

    response = client.put(
        f"/api/plantillas/{planta_id}",
        json={"nombre": "New"},
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["nombre"] == "New"


def test_delete_plantilla(client, user_data):
    headers = get_auth_header(client, user_data)
    create_response = client.post(
        "/api/plantillas",
        json={"nombre": "Delete", "slug": "delete"},
        headers=headers
    )
    planta_id = create_response.json()["id"]

    response = client.delete(f"/api/plantillas/{planta_id}", headers=headers)

    assert response.status_code == 200

    get_response = client.get(f"/api/plantillas/{planta_id}")
    assert get_response.status_code == 404