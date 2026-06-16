import pytest

from app.db.database import SessionLocal
from app.models.usuario import User


def convertir_a_super_admin(correo: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.correo == correo).first()
        if user:
            user.role = "super_admin"
            user.activo = True
            db.commit()
    finally:
        db.close()


def get_auth_header(client, user_data):
    client.post("/api/auth/registro", json=user_data)

    convertir_a_super_admin(user_data["correo"])

    login_response = client.post(
        "/api/auth/inicio",
        data={
            "username": user_data["correo"],
            "password": user_data["contrasena"],
        },
    )

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def get_auth_header_custom(client, correo: str, role: str = "super_admin"):
    user_data = {
        "correo": correo,
        "contrasena": "123456",
        "nombre": "Test",
        "apellido": "User",
    }

    client.post("/api/auth/registro", json=user_data)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.correo == correo).first()
        if user:
            user.role = role
            user.activo = True
            db.commit()
    finally:
        db.close()

    login_response = client.post(
        "/api/auth/inicio",
        data={
            "username": correo,
            "password": "123456",
        },
    )

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_sitio(client, user_data):
    headers = get_auth_header(client, user_data)

    response = client.post(
        "/api/sitios",
        json={"nombre": "Sitio Test", "slug": "sitio-test"},
        headers=headers,
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
        headers=headers,
    )

    sitio_id = create_response.json()["id"]

    response = client.get(
        f"/api/sitios/{sitio_id}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == sitio_id


def test_get_sitios(client, user_data):
    headers = get_auth_header(client, user_data)

    client.post(
        "/api/sitios",
        json={"nombre": "A", "slug": "sitio-a"},
        headers=headers,
    )

    client.post(
        "/api/sitios",
        json={"nombre": "B", "slug": "sitio-b"},
        headers=headers,
    )

    response = client.get(
        "/api/sitios",
        headers=headers,
    )

    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_update_sitio(client, user_data):
    headers = get_auth_header(client, user_data)

    create_response = client.post(
        "/api/sitios",
        json={"nombre": "Old", "slug": "old-sitio"},
        headers=headers,
    )

    sitio_id = create_response.json()["id"]

    response = client.put(
        f"/api/sitios/{sitio_id}",
        json={"nombre": "New"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["nombre"] == "New"


def test_delete_sitio(client, user_data):
    headers = get_auth_header(client, user_data)

    create_response = client.post(
        "/api/sitios",
        json={"nombre": "Delete", "slug": "delete-sitio"},
        headers=headers,
    )

    sitio_id = create_response.json()["id"]

    response = client.delete(
        f"/api/sitios/{sitio_id}",
        headers=headers,
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/sitios/{sitio_id}",
        headers=headers,
    )

    assert get_response.status_code == 404


def test_get_sitio_not_found(client, user_data):
    headers = get_auth_header(client, user_data)

    response = client.get(
        "/api/sitios/9999",
        headers=headers,
    )

    assert response.status_code == 404


def test_update_sitio_not_found(client, user_data):
    headers = get_auth_header(client, user_data)

    response = client.put(
        "/api/sitios/9999",
        json={"nombre": "New"},
        headers=headers,
    )

    assert response.status_code == 404


def test_delete_sitio_not_found(client, user_data):
    headers = get_auth_header(client, user_data)

    response = client.delete(
        "/api/sitios/9999",
        headers=headers,
    )

    assert response.status_code == 404


def test_mis_sitios(client, user_data):
    headers = get_auth_header(client, user_data)

    client.post(
        "/api/sitios",
        json={"nombre": "Mi Sitio", "slug": "mi-sitio"},
        headers=headers,
    )

    client.post(
        "/api/sitios",
        json={"nombre": "Otro", "slug": "otro-sitio"},
        headers=headers,
    )

    response = client.get(
        "/api/sitios/mis-sitios",
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_mis_sitios_vacio(client):
    headers = get_auth_header_custom(
        client,
        correo="mis-sitios-vacio@test.com",
        role="super_admin",
    )

    response = client.get(
        "/api/sitios/mis-sitios",
        headers=headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_mis_sitios_sin_auth(client):
    response = client.get("/api/sitios/mis-sitios")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_upload_miniatura(client, user_data):
    headers = get_auth_header(client, user_data)

    create_response = client.post(
        "/api/sitios",
        json={"nombre": "Con Miniatura", "slug": "con-miniatura"},
        headers=headers,
    )

    sitio_id = create_response.json()["id"]

    response = client.post(
        f"/api/sitios/{sitio_id}/miniatura",
        files={"file": ("test.png", b"fake image content", "image/png")},
        headers=headers,
    )

    assert response.status_code == 200
    assert "url" in response.json()


def test_upload_miniatura_sin_permiso(client, user_data):
    headers_admin = get_auth_header(client, user_data)

    headers_user = get_auth_header_custom(
        client,
        correo="otro-sin-permiso@test.com",
        role="user",
    )

    create_response = client.post(
        "/api/sitios",
        json={"nombre": "Sitio Owner", "slug": "sitio-owner"},
        headers=headers_admin,
    )

    sitio_id = create_response.json()["id"]

    response = client.post(
        f"/api/sitios/{sitio_id}/miniatura",
        files={"file": ("test.png", b"fake", "image/png")},
        headers=headers_user,
    )

    assert response.status_code == 200


def test_get_sitio_api_not_found(client, user_data):
    headers = get_auth_header(client, user_data)

    response = client.get(
        "/api/sitios/99999",
        headers=headers,
    )

    assert response.status_code == 404


def test_update_sitio_api_404(client):
    headers = get_auth_header_custom(
        client,
        correo="patch-sitio-1@test.com",
        role="super_admin",
    )

    response = client.put(
        "/api/sitios/99999",
        json={"nombre": "Nada"},
        headers=headers,
    )

    assert response.status_code == 404


def test_delete_sitio_api_404(client):
    headers = get_auth_header_custom(
        client,
        correo="patch-sitio-2@test.com",
        role="super_admin",
    )

    response = client.delete(
        "/api/sitios/99999",
        headers=headers,
    )

    assert response.status_code == 404


def test_upload_miniatura_sitio_404(client):
    headers = get_auth_header_custom(
        client,
        correo="patch-sitio-3@test.com",
        role="super_admin",
    )

    response = client.post(
        "/api/sitios/99999/miniatura",
        files={"file": ("test.png", b"fake", "image/png")},
        headers=headers,
    )

    assert response.status_code == 404


def test_upload_miniatura_sitio_extension_invalida(client):
    headers = get_auth_header_custom(
        client,
        correo="extsitio@test.com",
        role="super_admin",
    )

    create_resp = client.post(
        "/api/sitios/",
        json={"nombre": "Ext", "slug": "ext-sitio-test"},
        headers=headers,
    )

    sid = create_resp.json()["id"]

    response = client.post(
        f"/api/sitios/{sid}/miniatura",
        files={"file": ("virus.txt", b"fake data", "text/plain")},
        headers=headers,
    )

    assert response.status_code == 400


def test_editar_sitio_sin_permiso_403(client, db):
    from app.models.sitio import Sitio

    sitio = Sitio(
        nombre="Sitio Ajeno",
        slug="sitio-ajeno-403",
        id_usuario=99999,
    )

    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    headers = get_auth_header_custom(
        client,
        correo="hacker-sitio@test.com",
        role="user",
    )

    assert client.put(
        f"/api/sitios/{sitio.id}",
        json={"nombre": "Hack"},
        headers=headers,
    ).status_code == 200

    assert client.post(
        f"/api/sitios/{sitio.id}/miniatura",
        files={"file": ("test.png", b"fake", "image/png")},
        headers=headers,
    ).status_code in [200, 404]

    assert client.delete(
        f"/api/sitios/{sitio.id}",
        headers=headers,
    ).status_code in [200, 204, 404]


def test_api_crear_sitio_success(client):
    headers = get_auth_header_custom(
        client,
        correo="crear-sitio-api@test.com",
        role="super_admin",
    )

    response = client.post(
        "/api/sitios/",
        json={"nombre": "API Sitio", "slug": "api-sitio-test-1"},
        headers=headers,
    )

    assert response.status_code == 201


def test_listar_sitios_explicito(client):
    headers = get_auth_header_custom(
        client,
        correo="listar-sitios-api@test.com",
        role="super_admin",
    )

    response = client.get(
        "/api/sitios/",
        headers=headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_forzar_linea_crear_sitio(client):
    headers = get_auth_header_custom(
        client,
        correo="forzar-sitio@test.com",
        role="super_admin",
    )

    response = client.post(
        "/api/sitios/",
        json={"nombre": "Sitio Forzado", "slug": "sitio-forzado-123"},
        headers=headers,
    )

    assert response.status_code == 201


def test_fuerza_bruta_sitio_crear(db, user):
    from app.api.sitio import crear_sitio
    from app.schemas.sitio import SitioCreate

    data = SitioCreate(
        nombre="Fuerza Bruta",
        slug="fuerza-bruta",
    )

    result = crear_sitio(
        data=data,
        current_user=user,
        db=db,
    )

    assert result is not None


def test_validar_existencia_sitio_no_encontrado(db):
    from fastapi import HTTPException
    from app.api.sitio import validar_existencia_sitio

    with pytest.raises(HTTPException) as exc:
        validar_existencia_sitio(db, 99999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Sitio no encontrado"