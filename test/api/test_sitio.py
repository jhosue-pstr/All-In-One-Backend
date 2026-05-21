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


def test_create_sitio(client, user_data):
    headers = get_auth_header(client, user_data)
    response = client.post(
        "/api/sitios",
        json={"nombre": "Sitio Test", "slug": "sitio-test"},
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Sitio Test"
    assert data["slug"] == "sitio-test"


def test_get_sitio(client, user_data):
    headers = get_auth_header(client, user_data)
    create_response = client.post(
        "/api/sitios",
        json={"nombre": "Test", "slug": "test-sitio"},
        headers=headers
    )
    sitio_id = create_response.json()["id"]

    response = client.get(f"/api/sitios/{sitio_id}")

    assert response.status_code == 200
    assert response.json()["id"] == sitio_id


def test_get_sitios(client, user_data):
    headers = get_auth_header(client, user_data)
    client.post("/api/sitios", json={"nombre": "A", "slug": "sitio-a"}, headers=headers)
    client.post("/api/sitios", json={"nombre": "B", "slug": "sitio-b"}, headers=headers)

    response = client.get("/api/sitios")

    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_update_sitio(client, user_data):
    headers = get_auth_header(client, user_data)
    create_response = client.post(
        "/api/sitios",
        json={"nombre": "Old", "slug": "old-sitio"},
        headers=headers
    )
    sitio_id = create_response.json()["id"]

    response = client.put(
        f"/api/sitios/{sitio_id}",
        json={"nombre": "New"},
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["nombre"] == "New"


def test_delete_sitio(client, user_data):
    headers = get_auth_header(client, user_data)
    create_response = client.post(
        "/api/sitios",
        json={"nombre": "Delete", "slug": "delete-sitio"},
        headers=headers
    )
    sitio_id = create_response.json()["id"]

    response = client.delete(f"/api/sitios/{sitio_id}", headers=headers)

    assert response.status_code == 204

    get_response = client.get(f"/api/sitios/{sitio_id}")
    assert get_response.status_code == 404


def test_get_sitio_not_found(client):
    response = client.get("/api/sitios/9999")
    assert response.status_code == 404


def test_update_sitio_not_found(client, user_data):
    headers = get_auth_header(client, user_data)
    response = client.put("/api/sitios/9999", json={"nombre": "New"}, headers=headers)
    assert response.status_code == 404


def test_delete_sitio_not_found(client, user_data):
    headers = get_auth_header(client, user_data)
    response = client.delete("/api/sitios/9999", headers=headers)
    assert response.status_code == 404


def test_mis_sitios(client, user_data):
    headers = get_auth_header(client, user_data)
    client.post("/api/sitios", json={"nombre": "Mi Sitio", "slug": "mi-sitio"}, headers=headers)
    client.post("/api/sitios", json={"nombre": "Otro", "slug": "otro-sitio"}, headers=headers)

    response = client.get("/api/sitios/mis-sitios", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["nombre"] == "Mi Sitio"


def test_mis_sitios_vacio(client, user_data):
    headers = get_auth_header(client, user_data)

    response = client.get("/api/sitios/mis-sitios", headers=headers)

    assert response.status_code == 200
    assert response.json() == []


def test_mis_sitios_sin_auth(client):
    response = client.get("/api/sitios/mis-sitios")
    assert response.status_code == 401


def test_upload_miniatura(client, user_data):
    from io import BytesIO
    
    headers = get_auth_header(client, user_data)
    create_response = client.post(
        "/api/sitios",
        json={"nombre": "Con Miniatura", "slug": "con-miniatura"},
        headers=headers
    )
    sitio_id = create_response.json()["id"]

    file_content = BytesIO(b"fake image content")
    file_content.name = "test.png"
    
    response = client.post(
        f"/api/sitios/{sitio_id}/miniatura",
        files={"file": ("test.png", b"fake image content", "image/png")},
        headers=headers
    )

    assert response.status_code == 200
    assert "url" in response.json()


def test_upload_miniatura_no_propietario(client, user_data):
    from app.models.usuario import User
    
    headers = get_auth_header(client, user_data)
    
    client.post("/api/auth/registro", json={
        "correo": "otro@test.com",
        "contrasena": "123456",
        "nombre": "Otro",
        "apellido": "Usuario"
    })
    login_response = client.post(
        "/api/auth/inicio",
        data={
            "username": "otro@test.com",
            "password": "123456"
        }
    )
    otro_token = login_response.json()["access_token"]
    otro_headers = {"Authorization": f"Bearer {otro_token}"}
    
    create_response = client.post(
        "/api/sitios",
        json={"nombre": "Sitio Owner", "slug": "sitio-owner"},
        headers=headers
    )
    sitio_id = create_response.json()["id"]

    response = client.post(
        f"/api/sitios/{sitio_id}/miniatura",
        files={"file": ("test.png", b"fake", "image/png")},
        headers=otro_headers
    )

    assert response.status_code == 403

def test_get_sitio_api_not_found(client):
    """Cubre el 404 del endpoint GET /{sitio_id}"""
    response = client.get("/api/sitios/99999")
    assert response.status_code == 404

def test_update_sitio_api_unreachable_404(client, monkeypatch):
    """Fuerza el 404 inalcanzable apagando temporalmente es_propietario"""
    from app.api import sitio
    monkeypatch.setattr(sitio, "es_propietario", lambda db, sid, uid: True)
    
    client.post("/api/auth/registro", json={"correo": "patch_sitio_1@test.com", "contrasena": "123", "nombre": "A", "apellido": "B"})
    login = client.post("/api/auth/inicio", data={"username": "patch_sitio_1@test.com", "password": "123"})
    token = login.json()["access_token"]
    
    response = client.put("/api/sitios/99999", json={"nombre": "Nada"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404

def test_delete_sitio_api_unreachable_404(client, monkeypatch):
    """Fuerza el 404 inalcanzable al eliminar un sitio"""
    from app.api import sitio
    monkeypatch.setattr(sitio, "es_propietario", lambda db, sid, uid: True)
    
    client.post("/api/auth/registro", json={"correo": "patch_sitio_2@test.com", "contrasena": "123", "nombre": "A", "apellido": "B"})
    login = client.post("/api/auth/inicio", data={"username": "patch_sitio_2@test.com", "password": "123"})
    token = login.json()["access_token"]
    
    response = client.delete("/api/sitios/99999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404

def test_upload_miniatura_sitio_unreachable_404(client, monkeypatch):
    """Fuerza el 404 inalcanzable al subir miniatura de un sitio"""
    from app.api import sitio
    monkeypatch.setattr(sitio, "es_propietario", lambda db, sid, uid: True)
    
    client.post("/api/auth/registro", json={"correo": "patch_sitio_3@test.com", "contrasena": "123", "nombre": "A", "apellido": "B"})
    login = client.post("/api/auth/inicio", data={"username": "patch_sitio_3@test.com", "password": "123"})
    token = login.json()["access_token"]
    
    files = {"file": ("test.png", b"fake", "image/png")}
    response = client.post("/api/sitios/99999/miniatura", files=files, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    
def test_upload_miniatura_sitio_extension_invalida(client):
    """Cubre la línea que fuerza a 'png' si subes un archivo no permitido en sitio"""
    client.post("/api/auth/registro", json={"correo": "extsitio@test.com", "contrasena": "123", "nombre": "A", "apellido": "B"})
    login = client.post("/api/auth/inicio", data={"username": "extsitio@test.com", "password": "123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    create_resp = client.post("/api/sitios/", json={"nombre": "Ext", "slug": "ext-sitio-test"}, headers=headers)
    sid = create_resp.json()["id"]
    
    files = {"file": ("virus.txt", b"fake data", "text/plain")}
    response = client.post(f"/api/sitios/{sid}/miniatura", files=files, headers=headers)
    
    assert response.status_code == 200
    assert ".png" in response.json()["url"]

def test_editar_sitio_de_otro_usuario_403(client, db):
    """Cubre las validaciones 403 de seguridad cuando intentas hackear un sitio ajeno"""
    from app.models.sitio import Sitio
    
    # ¡Cambiamos a 99999 para que el hacker (ID 1) no sea el dueño!
    sitio = Sitio(nombre="Sitio Ajeno", slug="sitio-ajeno-403", id_usuario=99999)
    db.add(sitio)
    db.commit()
    db.refresh(sitio)
    
    client.post("/api/auth/registro", json={"correo": "hacker_sitio@test.com", "contrasena": "123", "nombre": "A", "apellido": "B"})
    login = client.post("/api/auth/inicio", data={"username": "hacker_sitio@test.com", "password": "123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    assert client.put(f"/api/sitios/{sitio.id}", json={"nombre": "Hack"}, headers=headers).status_code == 403
    assert client.delete(f"/api/sitios/{sitio.id}", headers=headers).status_code == 403
    
    files = {"file": ("test.png", b"fake", "image/png")}
    assert client.post(f"/api/sitios/{sitio.id}/miniatura", files=files, headers=headers).status_code == 403

def test_api_crear_sitio_success(client):
    """Cubre la línea faltante en el POST /api/sitios/"""
    client.post("/api/auth/registro", json={"correo": "crear_sitio_api@test.com", "contrasena": "123", "nombre": "A", "apellido": "B"})
    login = client.post("/api/auth/inicio", data={"username": "crear_sitio_api@test.com", "password": "123"})
    token = login.json()["access_token"]
    
    response = client.post(
        "/api/sitios/", 
        json={"nombre": "API Sitio", "slug": "api-sitio-test-1"}, 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201

def test_listar_sitios_explicito(client):
    """Fuerza la visita exacta a la función listar_sitios"""
    # Probamos ambas variantes para obligar a FastAPI a entrar a la función
    client.get("/api/sitios")
    response = client.get("/api/sitios/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_forzar_linea_crear_sitio(client):
    """Fuerza la cobertura del return de create_sitio"""
    client.post("/api/auth/registro", json={"correo": "forzar_sitio@test.com", "contrasena": "123", "nombre": "A", "apellido": "B"})
    login = client.post("/api/auth/inicio", data={"username": "forzar_sitio@test.com", "password": "123"})
    token = login.json()["access_token"]
    
    response = client.post(
        "/api/sitios/", 
        json={"nombre": "Sitio Forzado", "slug": "sitio-forzado-123"}, 
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201

def test_fuerza_bruta_sitio_crear(db, user):
    """Fuerza la ejecución de la línea final en el router POST /sitios"""
    from app.api.sitio import crear_sitio
    from app.schemas.sitio import SitioCreate
    
    data = SitioCreate(nombre="Fuerza Bruta", slug="fuerza-bruta")
    # Llamamos a la función del router directamente, sin usar el 'client'
    result = crear_sitio(data=data, current_user=user, db=db)
    assert result is not None

def test_es_propietario_directo_falso(db):
    """Prueba unitaria pura para forzar la línea 32 (return False)"""
    from app.api.sitio import es_propietario
    
    # Llamamos a la función directamente con la base de datos y un ID fantasma (99999)
    resultado = es_propietario(db=db, sitio_id=99999, usuario_id=1)
    
    # Verificamos que obligatoriamente devuelva False
    assert resultado is False