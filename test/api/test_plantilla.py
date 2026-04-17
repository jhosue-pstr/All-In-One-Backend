import pytest


def test_create_plantilla(client):
    response = client.post(
        "/api/plantillas",
        json={"nombre": "Plantilla 1", "slug": "plantilla-1"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Plantilla 1"
    assert data["slug"] == "plantilla-1"


def test_get_plantilla(client):
    create_response = client.post(
        "/api/plantillas",
        json={"nombre": "Test", "slug": "test"}
    )
    planta_id = create_response.json()["id"]

    response = client.get(f"/api/plantillas/{planta_id}")

    assert response.status_code == 200
    assert response.json()["id"] == planta_id


def test_get_plantillas(client):
    client.post("/api/plantillas", json={"nombre": "A", "slug": "a"})
    client.post("/api/plantillas", json={"nombre": "B", "slug": "b"})

    response = client.get("/api/plantillas")

    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_update_plantilla(client):
    create_response = client.post(
        "/api/plantillas",
        json={"nombre": "Old", "slug": "old"}
    )
    planta_id = create_response.json()["id"]

    response = client.put(
        f"/api/plantillas/{planta_id}",
        json={"nombre": "New"}
    )

    assert response.status_code == 200
    assert response.json()["nombre"] == "New"


def test_delete_plantilla(client):
    create_response = client.post(
        "/api/plantillas",
        json={"nombre": "Delete", "slug": "delete"}
    )
    planta_id = create_response.json()["id"]

    response = client.delete(f"/api/plantillas/{planta_id}")

    assert response.status_code == 200

    get_response = client.get(f"/api/plantillas/{planta_id}")
    assert get_response.status_code == 404