import pytest
import uuid

from app.db.database import SessionLocal
from app.models.usuario import User


def convertir_rol(correo: str, role: str = "super_admin"):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.correo == correo).first()
        if user:
            user.role = role
            user.activo = True
            db.commit()
    finally:
        db.close()


def get_auth_header(client, user_data, role: str = "super_admin"):
    client.post("/api/auth/registro", json=user_data)

    convertir_rol(user_data["correo"], role)

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

    convertir_rol(correo, role)

    login_response = client.post(
        "/api/auth/inicio",
        data={
            "username": correo,
            "password": "123456",
        },
    )

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_agregar_modulo_a_sitio(client, user_data):
    headers = get_auth_header(client, user_data, role="super_admin")
    uid = uuid.uuid4().hex[:8]

    modulo_response = client.post(
        "/api/modulos",
        json={
            "nombre": "Blog",
            "slug": f"blog-api-{uid}",
            "tipo": "content",
        },
        headers=headers,
    )

    assert modulo_response.status_code in [200, 201]
    modulo_id = modulo_response.json()["id"]

    sitio_response = client.post(
        "/api/sitios",
        json={
            "nombre": "Sitio Test",
            "slug": f"sitio-api-{uid}",
        },
        headers=headers,
    )

    assert sitio_response.status_code == 201
    sitio_id = sitio_response.json()["id"]

    response = client.post(
        f"/api/sitios/{sitio_id}/modulos/{modulo_id}",
        headers=headers,
    )

    assert response.status_code == 200


def test_quitar_modulo_de_sitio(client, user_data):
    headers = get_auth_header(client, user_data, role="super_admin")
    uid = uuid.uuid4().hex[:8]

    modulo_response = client.post(
        "/api/modulos",
        json={
            "nombre": "Blog2",
            "slug": f"blog2-api-{uid}",
            "tipo": "content",
        },
        headers=headers,
    )

    assert modulo_response.status_code in [200, 201]
    modulo_id = modulo_response.json()["id"]

    sitio_response = client.post(
        "/api/sitios",
        json={
            "nombre": "Sitio Test2",
            "slug": f"sitio2-api-{uid}",
        },
        headers=headers,
    )

    assert sitio_response.status_code == 201
    sitio_id = sitio_response.json()["id"]

    client.post(
        f"/api/sitios/{sitio_id}/modulos/{modulo_id}",
        headers=headers,
    )

    response = client.delete(
        f"/api/sitios/{sitio_id}/modulos/{modulo_id}",
        headers=headers,
    )

    assert response.status_code == 200


def test_get_modulos_del_sitio(client, user_data):
    headers = get_auth_header(client, user_data, role="super_admin")
    uid = uuid.uuid4().hex[:8]

    modulo_response = client.post(
        "/api/modulos",
        json={
            "nombre": "Blog3",
            "slug": f"blog3-api-{uid}",
            "tipo": "content",
        },
        headers=headers,
    )

    assert modulo_response.status_code in [200, 201]
    modulo_id = modulo_response.json()["id"]

    sitio_response = client.post(
        "/api/sitios",
        json={
            "nombre": "Sitio Test3",
            "slug": f"sitio3-api-{uid}",
        },
        headers=headers,
    )

    assert sitio_response.status_code == 201
    sitio_id = sitio_response.json()["id"]

    client.post(
        f"/api/sitios/{sitio_id}/modulos/{modulo_id}",
        headers=headers,
    )

    response = client.get(
        f"/api/sitios/{sitio_id}/modulos",
        headers=headers,
    )

    assert response.status_code == 200
    assert modulo_id in response.json()


def test_agregar_modulo_inexistente(client, user_data):
    headers = get_auth_header(client, user_data, role="super_admin")
    uid = uuid.uuid4().hex[:8]

    sitio_response = client.post(
        "/api/sitios",
        json={
            "nombre": "Sitio Test4",
            "slug": f"sitio4-api-{uid}",
        },
        headers=headers,
    )

    assert sitio_response.status_code == 201
    sitio_id = sitio_response.json()["id"]

    response = client.post(
        f"/api/sitios/{sitio_id}/modulos/999999",
        headers=headers,
    )

    assert response.status_code == 404


def test_get_modulos_sitio_inexistente(client, user_data):
    headers = get_auth_header(client, user_data, role="super_admin")

    response = client.get(
        "/api/sitios/999999/modulos",
        headers=headers,
    )

    assert response.status_code == 404


def test_listar_modulos_sitio_not_found(client):
    headers = get_auth_header_custom(
        client,
        correo=f"listar-modulos-{uuid.uuid4().hex[:8]}@test.com",
        role="super_admin",
    )

    response = client.get(
        "/api/sitios/999999/modulos/",
        headers=headers,
    )

    assert response.status_code == 404


def test_agregar_modulo_404(client):
    headers = get_auth_header_custom(
        client,
        correo=f"patch-mod-1-{uuid.uuid4().hex[:8]}@test.com",
        role="super_admin",
    )

    response = client.post(
        "/api/sitios/999999/modulos/999999",
        headers=headers,
    )

    assert response.status_code in [403, 404]


def test_quitar_modulo_404(client):
    headers = get_auth_header_custom(
        client,
        correo=f"patch-mod-2-{uuid.uuid4().hex[:8]}@test.com",
        role="super_admin",
    )

    response = client.delete(
        "/api/sitios/999999/modulos/999999",
        headers=headers,
    )

    assert response.status_code in [403, 404]


def test_modificar_modulos_sin_permiso_403(client, db):
    from app.models.sitio import Sitio

    sitio = Sitio(
        nombre="Sitio Ajeno Mod",
        slug=f"sitio-ajeno-mod-403-{uuid.uuid4().hex[:8]}",
        id_usuario=99999,
    )

    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    headers = get_auth_header_custom(
        client,
        correo=f"hacker-mod-{uuid.uuid4().hex[:8]}@test.com",
        role="user",
    )

    assert client.post(
        f"/api/sitios/{sitio.id}/modulos/1",
        headers=headers,
    ).status_code == 403

    assert client.delete(
        f"/api/sitios/{sitio.id}/modulos/1",
        headers=headers,
    ).status_code == 403


def test_api_listar_modulos_success(client, db):
    from app.models.sitio import Sitio

    headers = get_auth_header_custom(
        client,
        correo=f"listar-modulos-ok-{uuid.uuid4().hex[:8]}@test.com",
        role="super_admin",
    )

    sitio = Sitio(
        nombre="Sitio Lista Modulos",
        slug=f"sitio-lista-mod-{uuid.uuid4().hex[:8]}",
        id_usuario=1,
    )

    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    response = client.get(
        f"/api/sitios/{sitio.id}/modulos/",
        headers=headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_agregar_modulo_sin_permiso_403(client):
    headers = get_auth_header_custom(
        client,
        correo=f"prop-real-{uuid.uuid4().hex[:8]}@test.com",
        role="user",
    )

    response = client.post(
        "/api/sitios/999999/modulos/1",
        headers=headers,
    )

    assert response.status_code == 403