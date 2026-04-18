import pytest
from app.models.plantilla import Visibilidad


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


def test_create_plantilla_privada_por_defecto(client, user_data):
    headers = get_auth_header(client, user_data)
    response = client.post(
        "/api/plantillas",
        json={"nombre": "Plantilla 1", "slug": "plantilla-1"},
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Plantilla 1"
    assert data["visibilidad"] == "PRIVADA"
    assert data["id_usuario"] is not None


def test_create_plantilla_publica(client, user_data):
    headers = get_auth_header(client, user_data)
    response = client.post(
        "/api/plantillas",
        json={"nombre": "Publica", "slug": "publica", "visibilidad": "PUBLICA"},
        headers=headers
    )
    assert response.status_code == 201
    assert response.json()["visibilidad"] == "PUBLICA"


def test_get_publicas_sin_auth(client):
    response = client.get("/api/plantillas/publicas")
    assert response.status_code == 200


def test_get_mis_plantillas(client, user_data):
    headers = get_auth_header(client, user_data)
    client.post("/api/plantillas", json={"nombre": "Mi Plantilla", "slug": "mi-plantilla"}, headers=headers)

    response = client.get("/api/plantillas/mis-plantillas", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_publicas_y_mis_plantillas(client, user_data):
    headers = get_auth_header(client, user_data)

    client.post("/api/plantillas", json={"nombre": "Privada", "slug": "privada-test"}, headers=headers)
    client.post("/api/plantillas", json={"nombre": "Publica", "slug": "publica-test", "visibilidad": "PUBLICA"}, headers=headers)

    publicas = client.get("/api/plantillas/publicas").json()
    mias = client.get("/api/plantillas/mis-plantillas", headers=headers).json()

    assert any(p["visibilidad"] == "PUBLICA" for p in publicas)
    assert any(p["visibilidad"] == "PRIVADA" for p in mias)


def test_no_puede_editar_plantilla_de_otro(client, user_data):
    headers1 = get_auth_header(client, user_data)

    create_response = client.post(
        "/api/plantillas",
        json={"nombre": "User1 Plantilla", "slug": "user1-plantilla-test"},
        headers=headers1
    )
    plantilla_id = create_response.json()["id"]

    client.post("/api/auth/registro", json={"correo": "otro@test.com", "contrasena": "123456", "nombre": "Otro", "apellido": "User"})
    login2 = client.post("/api/auth/inicio", data={"username": "otro@test.com", "password": "123456"})
    headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}

    response = client.put(
        f"/api/plantillas/{plantilla_id}",
        json={"nombre": "Hack"},
        headers=headers2
    )

    assert response.status_code == 403


def test_no_puede_eliminar_plantilla_de_otro(client, user_data):
    headers1 = get_auth_header(client, user_data)

    create_response = client.post(
        "/api/plantillas",
        json={"nombre": "Delete Test", "slug": "delete-test-api"},
        headers=headers1
    )
    plantilla_id = create_response.json()["id"]

    client.post("/api/auth/registro", json={"correo": "otro2@test.com", "contrasena": "123456", "nombre": "Otro", "apellido": "User"})
    login2 = client.post("/api/auth/inicio", data={"username": "otro2@test.com", "password": "123456"})
    headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}

    response = client.delete(
        f"/api/plantillas/{plantilla_id}",
        headers=headers2
    )

    assert response.status_code == 403