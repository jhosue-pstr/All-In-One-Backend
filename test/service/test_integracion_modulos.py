import pytest
import uuid

from httpx import AsyncClient, ASGITransport

from app.main import app
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


@pytest.mark.asyncio
async def test_integracion_modulos():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        uid = uuid.uuid4().hex[:8]
        correo = f"integracion-{uid}@test.com"

        await ac.post(
            "/api/auth/registro",
            json={
                "correo": correo,
                "contrasena": "test123",
                "nombre": "Test",
                "apellido": "User",
            },
        )

        convertir_a_super_admin(correo)

        resp_login = await ac.post(
            "/api/auth/inicio",
            data={
                "username": correo,
                "password": "test123",
            },
        )

        assert resp_login.status_code == 200

        token = resp_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp_sitio = await ac.post(
            "/api/sitios/",
            json={
                "nombre": "Test Sitio",
                "slug": f"test-sitio-{uid}",
            },
            headers=headers,
        )

        assert resp_sitio.status_code == 201

        resp_blog = await ac.get("/api/modules/blog/1/posts")
        assert resp_blog.status_code == 200

        resp_store = await ac.get("/api/v1/sitios/1/tienda/productos")
        assert resp_store.status_code == 200