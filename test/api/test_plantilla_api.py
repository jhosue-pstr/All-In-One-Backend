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


def test_get_all_con_auth(client, user_data):
    headers = get_auth_header(client, user_data)
    
    client.post(
        "/api/plantillas",
        json={"nombre": "Mi Plantilla", "slug": "mi-plantilla-api"},
        headers=headers
    )
    
    response = client.get("/api/plantillas", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_create_plantilla(client, user_data):
    headers = get_auth_header(client, user_data)
    
    response = client.post(
        "/api/plantillas",
        json={"nombre": "Nueva Plantilla", "slug": "nueva-plantilla"},
        headers=headers
    )
    assert response.status_code == 201
    assert response.json()["nombre"] == "Nueva Plantilla"


def test_get_plantilla_not_found(client):
    response = client.get("/api/plantillas/99999")
    assert response.status_code == 404


def test_get_plantilla_success(client, user_data):
    headers = get_auth_header(client, user_data)
    
    create_response = client.post(
        "/api/plantillas",
        json={"nombre": "Test Get", "slug": "test-get"},
        headers=headers
    )
    plantilla_id = create_response.json()["id"]
    
    response = client.get(f"/api/plantillas/{plantilla_id}")
    assert response.status_code == 200


def test_update_plantilla_success(client, user_data):
    headers = get_auth_header(client, user_data)
    
    create_response = client.post(
        "/api/plantillas",
        json={"nombre": "Original", "slug": "original"},
        headers=headers
    )
    plantilla_id = create_response.json()["id"]
    
    response = client.put(
        f"/api/plantillas/{plantilla_id}",
        json={"nombre": "Actualizado"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["nombre"] == "Actualizado"


def test_update_plantilla_not_found(client, user_data):
    headers = get_auth_header(client, user_data)
    
    response = client.put(
        "/api/plantillas/99999",
        json={"nombre": "Test"},
        headers=headers
    )
    assert response.status_code in [403, 404]


def test_delete_plantilla_success(client, user_data):
    headers = get_auth_header(client, user_data)
    
    create_response = client.post(
        "/api/plantillas",
        json={"nombre": "Para Eliminar", "slug": "para-eliminar"},
        headers=headers
    )
    plantilla_id = create_response.json()["id"]
    
    response = client.delete(f"/api/plantillas/{plantilla_id}", headers=headers)
    assert response.status_code in [200, 204]


def test_delete_plantilla_not_found(client, user_data):
    headers = get_auth_header(client, user_data)
    
    response = client.delete("/api/plantillas/99999", headers=headers)
    assert response.status_code in [403, 404]


def test_upload_miniatura(client, user_data):
    headers = get_auth_header(client, user_data)
    
    create_response = client.post(
        "/api/plantillas",
        json={"nombre": "Con Miniatura", "slug": "con-miniatura"},
        headers=headers
    )
    plantilla_id = create_response.json()["id"]
    
    response = client.post(
        f"/api/plantillas/{plantilla_id}/miniatura",
        headers=headers,
        files={"file": ("test.png", b"fake-image-data", "image/png")}
    )
    assert response.status_code == 200
    assert "url" in response.json()