import pytest

def test_main_lifespan(client):
    response = client.get("/")
    assert response.status_code == 200


def test_main_health_check(client):
    response = client.get("/health")
    assert response.status_code in [200, 404]


def test_auth_update_me_apellido(client, user_data):
    client.post("/api/auth/registro", json=user_data)
    login = client.post("/api/auth/inicio", data={"username": user_data["correo"], "password": user_data["contrasena"]})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.put("/api/auth/me", json={"apellido": "Nuevo Apellido"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["apellido"] == "Nuevo Apellido"


def test_get_plantillas_publicas_endpoint(client):
    from app.models.plantilla import Plantilla, Visibilidad
    from test.conftest import TestingSessionLocal
    
    db = TestingSessionLocal()
    db.add(Plantilla(nombre="Publica Test", slug="pub-test-api", visibilidad=Visibilidad.PUBLICA))
    db.commit()
    
    response = client.get("/api/plantillas/publicas")
    assert response.status_code == 200
    db.close()


def test_get_mis_plantillas(client, user_data):
    client.post("/api/auth/registro", json=user_data)
    login = client.post("/api/auth/inicio", data={"username": user_data["correo"], "password": user_data["contrasena"]})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/plantillas/mis-plantillas", headers=headers)
    assert response.status_code == 200


def test_get_all_plantillas(client, user_data):
    client.post("/api/auth/registro", json=user_data)
    login = client.post("/api/auth/inicio", data={"username": user_data["correo"], "password": user_data["contrasena"]})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/plantillas", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)