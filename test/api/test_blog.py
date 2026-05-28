import pytest
import io
from httpx import AsyncClient, ASGITransport
from app.main import app
from unittest.mock import patch
from app.packages.modulos.blog import blog_module

BASE_URL = "http://test"
SITE_ID = 1


@pytest.mark.asyncio
async def test_blog_flujo_completo():
    """
    Prueba de integración completa del módulo Blog.
    Diseñada para alcanzar el 100% de coverage en routes.py y services.py
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:

        await ac.post("/api/sitios", json={"nombre": "Sitio Blog", "slug": "sitio-blog"})

        cat_data = {"name": "Tecnología y Programación!", "description": "Tech"}
        resp_cat = await ac.post(f"/api/modules/blog/{SITE_ID}/categories", json=cat_data)
        assert resp_cat.status_code == 200
        assert resp_cat.json()["slug"] == "tecnologia-y-programacion"

        post_data_1 = {
            "title": "Mi Primer Post",
            "content": "Contenido 1"
        }

        resp_post_1 = await ac.post(f"/api/modules/blog/{SITE_ID}/posts", json=post_data_1)
        assert resp_post_1.status_code == 200
        post_1 = resp_post_1.json()
        assert post_1["slug"] == "mi-primer-post"

        resp_post_2 = await ac.post(f"/api/modules/blog/{SITE_ID}/posts", json=post_data_1)
        assert resp_post_2.status_code == 200
        post_2 = resp_post_2.json()
        assert post_2["slug"] == "mi-primer-post-1"

        resp_upd_1 = await ac.put(
            f"/api/modules/blog/{SITE_ID}/posts/{post_1['id']}",
            json={"status": "published"}
        )
        assert resp_upd_1.status_code == 200

        resp_upd_2 = await ac.put(
            f"/api/modules/blog/{SITE_ID}/posts/{post_2['id']}",
            json={"status": "scheduled", "published_at": "2020-01-01T12:00:00Z"}
        )
        assert resp_upd_2.status_code == 200

        resp_get = await ac.get(f"/api/modules/blog/{SITE_ID}/posts/mi-primer-post")
        assert resp_get.status_code == 200
        assert resp_get.json()["id"] == post_1["id"]

        resp_get_404 = await ac.get(f"/api/modules/blog/{SITE_ID}/posts/slug-inventado")
        assert resp_get_404.status_code == 404

        resp_upd_404 = await ac.put(
            f"/api/modules/blog/{SITE_ID}/posts/9999",
            json={"title": "No"}
        )
        assert resp_upd_404.status_code == 404

        resp_list_all = await ac.get(f"/api/modules/blog/{SITE_ID}/posts")
        assert resp_list_all.status_code == 200
        assert len(resp_list_all.json()) >= 2

        resp_list_pub = await ac.get(f"/api/modules/blog/{SITE_ID}/posts?only_published=true")
        assert resp_list_pub.status_code == 200
        publicados = [p["id"] for p in resp_list_pub.json()]
        assert post_1["id"] in publicados
        assert post_2["id"] in publicados

        resp_del = await ac.delete(f"/api/modules/blog/{SITE_ID}/posts/{post_2['id']}")
        assert resp_del.status_code == 200

        resp_del_404 = await ac.delete(f"/api/modules/blog/{SITE_ID}/posts/9999")
        assert resp_del_404.status_code == 404

        await ac.post("/api/auth/registro", json={
            "correo": "blog@test.com",
            "contrasena": "test123",
            "nombre": "Blog",
            "apellido": "Tester"
        })

        resp_login = await ac.post("/api/auth/inicio", data={
            "username": "blog@test.com",
            "password": "test123"
        })

        token = resp_login.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        file_valid = {
            "file": ("imagen.png", io.BytesIO(b"fake image data"), "image/png")
        }

        resp_upload_ok = await ac.post(
            f"/api/modules/blog/{SITE_ID}/upload-image",
            files=file_valid,
            headers=auth_headers
        )

        assert resp_upload_ok.status_code == 200
        assert "url" in resp_upload_ok.json()

        file_invalid = {
            "file": ("virus.txt", io.BytesIO(b"hack"), "text/plain")
        }

        resp_upload_bad = await ac.post(
            f"/api/modules/blog/{SITE_ID}/upload-image",
            files=file_invalid,
            headers=auth_headers
        )

        assert resp_upload_bad.status_code == 400


@pytest.mark.asyncio
async def test_blog_excepciones_y_modulo():
    """
    Prueba diseñada para cubrir los casos borde faltantes y alcanzar el 100%.
    Cubre: __init__.py, module.py y el Error 500 en upload-image de routes.py.
    """
    modelos = blog_module.get_models()
    assert len(modelos) > 0

    esquemas = blog_module.get_schemas()
    assert len(esquemas) > 0

    blog_module.on_activate(site_id=1, db=None, config={})
    blog_module.on_deactivate(site_id=1, db=None)
    blog_module.on_install(db=None)

    menu = blog_module.get_admin_menu()
    assert isinstance(menu, list)

    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        await ac.post("/api/auth/registro", json={
            "correo": "blog500@test.com",
            "contrasena": "test123",
            "nombre": "Blog",
            "apellido": "Error"
        })

        resp_login = await ac.post("/api/auth/inicio", data={
            "username": "blog500@test.com",
            "password": "test123"
        })

        token = resp_login.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        file_valid = {
            "file": ("imagen2.png", io.BytesIO(b"fake data"), "image/png")
        }

        with patch("builtins.open", side_effect=OSError("Disco lleno simulado")):
            resp_500 = await ac.post(
                f"/api/modules/blog/{SITE_ID}/upload-image",
                files=file_valid,
                headers=auth_headers
            )

            assert resp_500.status_code == 500
            assert "Disco lleno simulado" in resp_500.json()["detail"]


def test_blog_services_publicados_y_slug_no_encontrado():
    from datetime import datetime, timedelta, timezone
    from fastapi import HTTPException
    from sqlalchemy.orm import Session as DBSession

    from app.db.database import engine
    from app.packages.modulos.blog.services import (
        create_post,
        get_posts_by_site,
        get_post_by_slug
    )
    from app.packages.modulos.blog.schemas import PostCreate
    from app.packages.modulos.blog.models import PostStatus

    site_id = 1

    with DBSession(engine) as db:
        post_publicado = create_post(
            db,
            site_id,
            PostCreate(
                title="Post Publicado Service",
                content="Contenido publicado",
                status=PostStatus.PUBLISHED
            )
        )

        create_post(
            db,
            site_id,
            PostCreate(
                title="Post Programado Service",
                content="Contenido programado",
                status=PostStatus.SCHEDULED,
                published_at=datetime.now(timezone.utc) - timedelta(days=1)
            )
        )

        create_post(
            db,
            site_id,
            PostCreate(
                title="Post Borrador Service",
                content="Contenido borrador",
                status=PostStatus.DRAFT
            )
        )

        publicados = get_posts_by_site(
            db,
            site_id,
            only_published=True
        )

        slugs = [p.slug for p in publicados]

        assert post_publicado.slug in slugs
        assert any("post-programado-service" in slug for slug in slugs)
        assert not any("post-borrador-service" in slug for slug in slugs)

        post_encontrado = get_post_by_slug(
            db,
            site_id,
            post_publicado.slug
        )

        assert post_encontrado.id == post_publicado.id
        assert post_encontrado.slug == post_publicado.slug

        try:
            get_post_by_slug(db, site_id, "slug-no-existe")
            assert False
        except HTTPException as e:
            assert e.status_code == 404
            assert e.detail == "Artículo no encontrado"


def test_blog_routes_is_post_publicly_available():
    from datetime import datetime, timedelta
    from unittest.mock import MagicMock

    from app.packages.modulos.blog.routes import is_post_publicly_available

    post_scheduled_pasado = MagicMock()
    post_scheduled_pasado.status = "scheduled"
    post_scheduled_pasado.published_at = datetime.utcnow() - timedelta(days=1)

    assert is_post_publicly_available(post_scheduled_pasado) is True

    post_scheduled_futuro = MagicMock()
    post_scheduled_futuro.status = "scheduled"
    post_scheduled_futuro.published_at = datetime.utcnow() + timedelta(days=1)

    assert is_post_publicly_available(post_scheduled_futuro) is False

    post_draft = MagicMock()
    post_draft.status = "draft"
    post_draft.published_at = None

    assert is_post_publicly_available(post_draft) is False


def test_blog_route_post_no_disponible_directo():
    from unittest.mock import MagicMock, patch
    from fastapi import HTTPException

    from app.packages.modulos.blog.routes import get_post_route

    post = MagicMock()
    post.status = "draft"
    post.published_at = None

    result = MagicMock()
    result.scalar_one_or_none.return_value = post

    db = MagicMock()
    db.execute.return_value = result

    with patch(
        "app.packages.modulos.blog.routes.is_post_publicly_available",
        return_value=False
    ):
        try:
            get_post_route(1, "post-draft", db)
            assert False
        except HTTPException as e:
            assert e.status_code == 404
            assert e.detail == "Artículo no disponible"


@pytest.mark.asyncio
async def test_blog_upload_image_validaciones_extra():
    import uuid
    from unittest.mock import MagicMock
    from fastapi import HTTPException
    from app.packages.modulos.blog.routes import upload_blog_image

    correo = f"blog-upload-extra-{uuid.uuid4().hex[:8]}@test.com"

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        await ac.post(
            "/api/auth/registro",
            json={
                "correo": correo,
                "contrasena": "test123",
                "nombre": "Blog",
                "apellido": "Upload"
            }
        )

        resp_login = await ac.post(
            "/api/auth/inicio",
            data={
                "username": correo,
                "password": "test123"
            }
        )

        token = resp_login.json()["access_token"]

        headers = {
            "Authorization": f"Bearer {token}"
        }

        # Línea 208: filename vacío forzado directamente en la función
        archivo_sin_nombre = MagicMock()
        archivo_sin_nombre.content_type = "image/png"
        archivo_sin_nombre.filename = ""

        try:
            await upload_blog_image(
                site_id=1,
                file=archivo_sin_nombre,
                db=None,
                current_user=MagicMock()
            )
            assert False
        except HTTPException as e:
            assert e.status_code == 400
            assert e.detail == "El archivo no tiene nombre válido"

        # Línea 216: extensión inválida aunque content_type sea imagen
        files_extension_mala = {
            "file": ("imagen.txt", io.BytesIO(b"fake data"), "image/png")
        }

        resp_extension_mala = await ac.post(
            "/api/modules/blog/1/upload-image",
            files=files_extension_mala,
            headers=headers
        )

        assert resp_extension_mala.status_code == 400
        assert resp_extension_mala.json()["detail"] == "Extensión de imagen no permitida"

        # Línea 229: archivo vacío
        files_vacio = {
            "file": ("imagen.png", io.BytesIO(b""), "image/png")
        }

        resp_vacio = await ac.post(
            "/api/modules/blog/1/upload-image",
            files=files_vacio,
            headers=headers
        )

        assert resp_vacio.status_code == 400
        assert resp_vacio.json()["detail"] == "El archivo está vacío"