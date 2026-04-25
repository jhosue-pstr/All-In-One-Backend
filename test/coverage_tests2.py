import pytest
from app.service.sitio_modulo import agregar_modulo_a_sitio, get_modulos_del_sitio


def test_sitio_modulo_return_none(db):
    assert agregar_modulo_a_sitio(db, 99999, 99999) is None
    assert get_modulos_del_sitio(db, 99999) is None


def test_sitio_modulo_api_not_found(client, user_data):
    client.post("/api/auth/registro", json=user_data)
    login = client.post("/api/auth/inicio", data={"username": user_data["correo"], "password": user_data["contrasena"]})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/api/sitios/99999/modulos/1", headers=headers)
    assert response.status_code == 404


def test_auth_user_no_existe(db):
    from app.api.auth import authenticate_user
    
    result = authenticate_user(db, "noexiste@test.com", "pass")
    assert result is None


def test_usuario_sitio_verify_token_none(db):
    from app.packages.modulos.SiteAuth.services.usuario_sitio import verify_token_usuario_sitio
    
    result = verify_token_usuario_sitio(db, "invalid-token")
    assert result is None


def test_publico_injectar_recursos_sin_body():
    from app.api.publico import injectar_recursos
    
    result = injectar_recursos("", "", "")
    assert "<html>" in result


def test_get_sitio_not_found_api(client):
    response = client.get("/api/sitios/99999")
    assert response.status_code == 404


def test_upload_sitio_miniatura_extension_invalida(client, user_data):
    client.post("/api/auth/registro", json=user_data)
    login = client.post("/api/auth/inicio", data={"username": user_data["correo"], "password": user_data["contrasena"]})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    create_response = client.post(
        "/api/sitios",
        json={"nombre": "Test Ext", "slug": "test-ext-sitio"},
        headers=headers
    )
    sitio_id = create_response.json()["id"]
    
    response = client.post(
        f"/api/sitios/{sitio_id}/miniatura",
        headers=headers,
        files={"file": ("test.txt", b"content", "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert ".png" in data["url"]


def test_get_sitios(db):
    from app.service.sitio import get_sitios
    result = get_sitios(db)
    assert isinstance(result, list)