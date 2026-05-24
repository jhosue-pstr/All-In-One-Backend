import pytest
from httpx import AsyncClient, ASGITransport # <-- Importar ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_integracion_modulos():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:

        await ac.post("/api/auth/registro", json={
            "correo": "test@test.com", "contrasena": "test123",
            "nombre": "Test", "apellido": "User"
        })
        resp_login = await ac.post("/api/auth/inicio", data={
            "username": "test@test.com", "password": "test123"
        })
        token = resp_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        await ac.post("/api/sitios", json={"nombre": "Test Sitio", "slug": "test-sitio"}, headers=headers)

        resp_blog = await ac.get("/modules/blog/1/posts")
        assert resp_blog.status_code == 200

        resp_store = await ac.get("/api/v1/sitios/1/tienda/productos")
        assert resp_store.status_code == 200