import pytest
from unittest.mock import AsyncMock, MagicMock, patch


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
    
    # 1. Usuario crea plantilla
    create_response = client.post(
        "/api/plantillas",
        json={"nombre": "Con Miniatura", "slug": "con-miniatura"},
        headers=headers
    )
    plantilla_id = create_response.json()["id"]
    
    # 2. Usuario sube miniatura a SU plantilla
    response = client.post(
        f"/api/plantillas/{plantilla_id}/miniatura",
        headers=headers,
        files={"file": ("test.png", b"fake-image-data", "image/png")}
    )
    
    # 3. Verificar
    assert response.status_code == 200
    assert "url" in response.json()  # ← LÍNEA 135 SE CUBRE AQUÍ


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

@pytest.mark.anyio
async def test_fuerza_bruta_miniatura_return(db, user):
    """Fuerza la ejecución del return final en upload_miniatura (ASÍNCRONO)
    
    Este test cubre la línea 135 que faltaba en app/api/plantilla.py
    Ahora usa 'await' correctamente para evitar el RuntimeWarning
    """
    from app.api.plantilla import upload_miniatura
    from fastapi import Request
    from starlette.datastructures import Headers
    
    # Creamos un archivo falso con el método read asíncrono
    class FakeUploadFile:
        filename = "test.png"
        
        async def read(self):
            return b"fake data"
            
    # Creamos un Request falso muy básico
    scope = {
        "type": "http",
        "headers": Headers({"host": "testserver"}).raw,
        "scheme": "http",
        "server": ("testserver", 80),
        "path": "/",
        "query_string": b"",
    }
    request = Request(scope)
    
    # Creamos una plantilla real en la base de datos
    from app.models.plantilla import Plantilla
    p = Plantilla(nombre="FB", slug="fb", id_usuario=user.id)
    db.add(p)
    db.commit()
    db.refresh(p)
    
    # LLAMAMOS AL ROUTER DIRECTAMENTE CON AWAIT (CORREGIDO)
    result = await upload_miniatura(
        plantilla_id=p.id,
        request=request,
        current_user=user,
        db=db,
        file=FakeUploadFile()
    )
    assert "url" in result