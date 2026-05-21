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


def test_update_plantilla_api_unreachable_404(client, monkeypatch):
    """Fuerza el 404 inalcanzable apagando temporalmente es_propietario con monkeypatch"""
    from app.api import plantilla
    monkeypatch.setattr(plantilla, "es_propietario", lambda db, pid, uid: True)
    
    client.post("/api/auth/registro", json={"correo": "patch1@test.com", "contrasena": "123", "nombre": "A", "apellido": "B"})
    login = client.post("/api/auth/inicio", data={"username": "patch1@test.com", "password": "123"})
    token = login.json()["access_token"]
    
    response = client.put("/api/plantillas/99999", json={"nombre": "Nada"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404

def test_upload_miniatura_not_found(client, monkeypatch):
    """Fuerza el 404 de la miniatura inalcanzable"""
    from app.api import plantilla
    monkeypatch.setattr(plantilla, "es_propietario", lambda db, pid, uid: True)
    
    client.post("/api/auth/registro", json={"correo": "patch2@test.com", "contrasena": "123", "nombre": "A", "apellido": "B"})
    login = client.post("/api/auth/inicio", data={"username": "patch2@test.com", "password": "123"})
    token = login.json()["access_token"]
    
    files = {"file": ("test.png", b"fake", "image/png")}
    response = client.post("/api/plantillas/99999/miniatura", files=files, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404

def test_upload_miniatura_extension_invalida(client):
    """Cubre la línea que fuerza a 'png' si subes un archivo no permitido"""
    client.post("/api/auth/registro", json={"correo": "ext@test.com", "contrasena": "123", "nombre": "A", "apellido": "B"})
    login = client.post("/api/auth/inicio", data={"username": "ext@test.com", "password": "123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    create_resp = client.post("/api/plantillas", json={"nombre": "Ext", "slug": "ext-test"}, headers=headers)
    pid = create_resp.json()["id"]
    
    # Subimos un archivo .txt prohibido
    files = {"file": ("virus.txt", b"fake data", "text/plain")}
    response = client.post(f"/api/plantillas/{pid}/miniatura", files=files, headers=headers)
    
    assert response.status_code == 200
    assert ".png" in response.json()["url"]  # El sistema debió convertir la extensión


def test_get_plantilla_api_not_found(client):
    """Cubre la línea faltante en el endpoint get_one (GET /plantillas/{id})"""
    response = client.get("/api/plantillas/99999")
    assert response.status_code == 404

def test_upload_miniatura_sin_extension_alguna(client):
    """Cubre el condicional 'else' cuando el archivo no tiene un punto en su nombre"""
    client.post("/api/auth/registro", json={"correo": "noext@test.com", "contrasena": "123", "nombre": "A", "apellido": "B"})
    login = client.post("/api/auth/inicio", data={"username": "noext@test.com", "password": "123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    create_resp = client.post("/api/plantillas", json={"nombre": "NoExt", "slug": "no-ext"}, headers=headers)
    pid = create_resp.json()["id"]
    
    # Subimos un archivo llamado 'archivofantasma' (SIN punto ni extensión)
    files = {"file": ("archivofantasma", b"fake data", "image/png")}
    response = client.post(f"/api/plantillas/{pid}/miniatura", files=files, headers=headers)
    
    assert response.status_code == 200
    assert ".png" in response.json()["url"]

def test_forzar_linea_subir_foto_plantilla(client):
    """Fuerza la cobertura del return final de upload_miniatura"""
    client.post("/api/auth/registro", json={"correo": "forzar_foto@test.com", "contrasena": "123", "nombre": "A", "apellido": "B"})
    login = client.post("/api/auth/inicio", data={"username": "forzar_foto@test.com", "password": "123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    create_resp = client.post("/api/plantillas", json={"nombre": "Foto Forzada", "slug": "foto-forzada"}, headers=headers)
    pid = create_resp.json()["id"]
    
    files = {"file": ("test.png", b"fake", "image/png")}
    response = client.post(f"/api/plantillas/{pid}/miniatura", files=files, headers=headers)
    assert response.status_code == 200

def test_plantillas_errores_403_sin_permiso(client):
    """Cubre las líneas de error 403 forzando a un usuario a editar la plantilla de otro"""
    
    # 1. Creamos al Usuario Propietario y su token
    client.post("/api/auth/registro", json={"correo": "dueno@test.com", "contrasena": "123", "nombre": "Dueño", "apellido": "A"})
    token_dueno = client.post("/api/auth/inicio", data={"username": "dueno@test.com", "password": "123"}).json()["access_token"]
    headers_dueno = {"Authorization": f"Bearer {token_dueno}"}

    # 2. El Propietario crea una plantilla
    resp_crear = client.post("/api/plantillas", json={"nombre": "Privado", "slug": "privado-403"}, headers=headers_dueno)
    pid = resp_crear.json()["id"]

    # 3. Creamos al Usuario "Intruso" y su token
    client.post("/api/auth/registro", json={"correo": "intruso@test.com", "contrasena": "123", "nombre": "Intruso", "apellido": "B"})
    token_intruso = client.post("/api/auth/inicio", data={"username": "intruso@test.com", "password": "123"}).json()["access_token"]
    headers_intruso = {"Authorization": f"Bearer {token_intruso}"}

    # 4. El Intruso intenta modificar la plantilla (ESTO DISPARA LOS RAISES 403)
    
    # A) Intenta hacer UPDATE
    resp_update = client.put(f"/api/plantillas/{pid}", json={"nombre": "Hackeado"}, headers=headers_intruso)
    assert resp_update.status_code == 403

    # B) Intenta subir MINIATURA
    files = {"file": ("test.png", b"fake data", "image/png")}
    resp_miniatura = client.post(f"/api/plantillas/{pid}/miniatura", files=files, headers=headers_intruso)
    assert resp_miniatura.status_code == 403
    
    # C) Intenta hacer DELETE
    resp_delete = client.delete(f"/api/plantillas/{pid}", headers=headers_intruso)
    assert resp_delete.status_code == 403