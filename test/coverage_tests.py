import pytest

def test_get_plantillas_publicas(db):
    from app.service.plantilla import get_plantillas_publicas
    from app.models.plantilla import Plantilla, Visibilidad
    
    db.add_all([
        Plantilla(nombre="Publica", slug="pub-test", visibilidad=Visibilidad.PUBLICA),
        Plantilla(nombre="Privada", slug="priv-test", visibilidad=Visibilidad.PRIVADA),
    ])
    db.commit()
    
    result = get_plantillas_publicas(db)
    assert all(p.visibilidad == Visibilidad.PUBLICA for p in result)


def test_update_plantilla_not_found(client, user_data):
    client.post("/api/auth/registro", json=user_data)
    login = client.post("/api/auth/inicio", data={"username": user_data["correo"], "password": user_data["contrasena"]})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.put("/api/plantillas/99999", json={"nombre": "Test"}, headers=headers)
    assert response.status_code in [403, 404]


def test_upload_miniatura_sin_permiso(client, user_data):
    client.post("/api/auth/registro", json=user_data)
    login = client.post("/api/auth/inicio", data={"username": user_data["correo"], "password": user_data["contrasena"]})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post(
        "/api/plantillas/99999/miniatura",
        headers=headers,
        files={"file": ("test.png", b"fake", "image/png")}
    )
    assert response.status_code in [403, 404]


def test_upload_miniatura_extension_invalida(client, user_data):
    client.post("/api/auth/registro", json=user_data)
    login = client.post("/api/auth/inicio", data={"username": user_data["correo"], "password": user_data["contrasena"]})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    create_response = client.post(
        "/api/plantillas",
        json={"nombre": "Test Ext", "slug": "test-ext"},
        headers=headers
    )
    plantilla_id = create_response.json()["id"]
    
    response = client.post(
        f"/api/plantillas/{plantilla_id}/miniatura",
        headers=headers,
        files={"file": ("test.exe", b"fake", "application/octet-stream")}
    )
    assert response.status_code == 200
    data = response.json()
    assert ".png" in data["url"]