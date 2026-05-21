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

def test_listar_modulos_sitio_not_found(client):
    """Cubre el 404 cuando se listan módulos de un sitio inexistente"""
    response = client.get("/api/sitios/99999/modulos/")
    assert response.status_code == 404

def test_agregar_modulo_unreachable_404(client, monkeypatch):
    """Fuerza el 404 inalcanzable al agregar un modulo"""
    from app.api import sitio_modulo
    monkeypatch.setattr(sitio_modulo, "es_propietario_sitio", lambda db, sid, uid: True)
    
    client.post("/api/auth/registro", json={"correo": "patch_mod_1@test.com", "contrasena": "123", "nombre": "A", "apellido": "B"})
    login = client.post("/api/auth/inicio", data={"username": "patch_mod_1@test.com", "password": "123"})
    token = login.json()["access_token"]
    
    response = client.post("/api/sitios/99999/modulos/99999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404

def test_quitar_modulo_unreachable_404(client, monkeypatch):
    """Fuerza el 404 inalcanzable al quitar un modulo"""
    from app.api import sitio_modulo
    monkeypatch.setattr(sitio_modulo, "es_propietario_sitio", lambda db, sid, uid: True)
    
    client.post("/api/auth/registro", json={"correo": "patch_mod_2@test.com", "contrasena": "123", "nombre": "A", "apellido": "B"})
    login = client.post("/api/auth/inicio", data={"username": "patch_mod_2@test.com", "password": "123"})
    token = login.json()["access_token"]
    
    response = client.delete("/api/sitios/99999/modulos/99999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404

def test_modificar_modulos_sitio_ajeno_403(client, db):
    """Cubre las validaciones 403 al intentar poner módulos en sitios ajenos"""
    from app.models.sitio import Sitio
    
    # ¡Cambiamos a 99999!
    sitio = Sitio(nombre="Sitio Ajeno Mod", slug="sitio-ajeno-mod-403", id_usuario=99999)
    db.add(sitio)
    db.commit()
    db.refresh(sitio)
    
    client.post("/api/auth/registro", json={"correo": "hacker_mod@test.com", "contrasena": "123", "nombre": "A", "apellido": "B"})
    login = client.post("/api/auth/inicio", data={"username": "hacker_mod@test.com", "password": "123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    assert client.post(f"/api/sitios/{sitio.id}/modulos/1", headers=headers).status_code == 403
    assert client.delete(f"/api/sitios/{sitio.id}/modulos/1", headers=headers).status_code == 403

def test_api_listar_modulos_success(client, db):
    """Cubre la línea faltante (el return feliz) en GET /api/sitios/{id}/modulos/"""
    from app.models.sitio import Sitio
    sitio = Sitio(nombre="Sitio Lista Modulos", slug="sitio-lista-mod", id_usuario=1)
    db.add(sitio)
    db.commit()
    db.refresh(sitio)
    
    response = client.get(f"/api/sitios/{sitio.id}/modulos/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_es_propietario_sitio_not_found_real(client):
    """Cubre la línea 25 comprobando que devuelva False si el sitio no existe de forma natural"""
    client.post("/api/auth/registro", json={"correo": "prop_real@test.com", "contrasena": "123", "nombre": "A", "apellido": "B"})
    login = client.post("/api/auth/inicio", data={"username": "prop_real@test.com", "password": "123"})
    token = login.json()["access_token"]
    
    # Al no usar monkeypatch, el sistema ejecuta la función real y la bloquea con un 403
    response = client.post("/api/sitios/99999/modulos/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403