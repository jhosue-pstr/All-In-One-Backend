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


def test_agregar_modulo_a_sitio(client, user_data):
    headers = get_auth_header(client, user_data)
    
    modulo_response = client.post(
        "/api/modulos",
        json={"nombre": "Blog", "slug": "blog-api", "tipo": "content"},
        headers=headers
    )
    modulo_id = modulo_response.json()["id"]
    
    sitio_response = client.post(
        "/api/sitios",
        json={"nombre": "Sitio Test", "slug": "sitio-api"},
        headers=headers
    )
    sitio_id = sitio_response.json()["id"]
    
    response = client.post(
        f"/api/sitios/{sitio_id}/modulos/{modulo_id}",
        headers=headers
    )
    assert response.status_code == 200


def test_quitar_modulo_de_sitio(client, user_data):
    headers = get_auth_header(client, user_data)
    
    modulo_response = client.post(
        "/api/modulos",
        json={"nombre": "Blog2", "slug": "blog2-api", "tipo": "content"},
        headers=headers
    )
    modulo_id = modulo_response.json()["id"]
    
    sitio_response = client.post(
        "/api/sitios",
        json={"nombre": "Sitio Test2", "slug": "sitio2-api"},
        headers=headers
    )
    sitio_id = sitio_response.json()["id"]
    
    client.post(f"/api/sitios/{sitio_id}/modulos/{modulo_id}", headers=headers)
    
    response = client.delete(f"/api/sitios/{sitio_id}/modulos/{modulo_id}", headers=headers)
    assert response.status_code == 200


def test_get_modulos_del_sitio(client, user_data):
    headers = get_auth_header(client, user_data)
    
    modulo_response = client.post(
        "/api/modulos",
        json={"nombre": "Blog3", "slug": "blog3-api", "tipo": "content"},
        headers=headers
    )
    modulo_id = modulo_response.json()["id"]
    
    sitio_response = client.post(
        "/api/sitios",
        json={"nombre": "Sitio Test3", "slug": "sitio3-api"},
        headers=headers
    )
    sitio_id = sitio_response.json()["id"]
    
    client.post(f"/api/sitios/{sitio_id}/modulos/{modulo_id}", headers=headers)
    
    response = client.get(f"/api/sitios/{sitio_id}/modulos")
    assert response.status_code == 200
    assert modulo_id in response.json()


def test_agregar_modulo_inexistente(client, user_data):
    headers = get_auth_header(client, user_data)
    
    sitio_response = client.post(
        "/api/sitios",
        json={"nombre": "Sitio Test4", "slug": "sitio4-api"},
        headers=headers
    )
    sitio_id = sitio_response.json()["id"]
    
    response = client.post(
        f"/api/sitios/{sitio_id}/modulos/9999",
        headers=headers
    )
    assert response.status_code == 404


def test_get_modulos_sitio_inexistente(client, user_data):
    headers = get_auth_header(client, user_data)
    response = client.get("/api/sitios/9999/modulos")
    assert response.status_code == 404