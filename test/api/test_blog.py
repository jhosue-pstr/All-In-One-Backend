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
    Diseñada para cubrir flujo principal de categorías, posts, publicación,
    búsqueda, eliminación y subida de imagen.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        await ac.post("/api/sitios", json={"nombre": "Sitio Blog", "slug": "sitio-blog"})

        cat_data = {"name": "Tecnología y Programación!", "description": "Tech"}
        resp_cat = await ac.post(f"/api/modules/blog/{SITE_ID}/categories", json=cat_data)
        assert resp_cat.status_code == 200
        assert resp_cat.json()["slug"] == "tecnologia-y-programacion"

        post_data_1 = {
            "title": "Mi Primer Post",
            "content": "Contenido 1",
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
            json={"status": "published"},
        )
        assert resp_upd_1.status_code == 200

        resp_upd_2 = await ac.put(
            f"/api/modules/blog/{SITE_ID}/posts/{post_2['id']}",
            json={"status": "scheduled", "published_at": "2020-01-01T12:00:00Z"},
        )
        assert resp_upd_2.status_code == 200

        resp_get = await ac.get(f"/api/modules/blog/{SITE_ID}/posts/mi-primer-post")
        assert resp_get.status_code == 200
        assert resp_get.json()["id"] == post_1["id"]

        resp_get_404 = await ac.get(f"/api/modules/blog/{SITE_ID}/posts/slug-inventado")
        assert resp_get_404.status_code == 404

        resp_upd_404 = await ac.put(
            f"/api/modules/blog/{SITE_ID}/posts/9999",
            json={"title": "No"},
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

        await ac.post(
            "/api/auth/registro",
            json={
                "correo": "blog@test.com",
                "contrasena": "test123",
                "nombre": "Blog",
                "apellido": "Tester",
            },
        )

        resp_login = await ac.post(
            "/api/auth/inicio",
            data={
                "username": "blog@test.com",
                "password": "test123",
            },
        )

        token = resp_login.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        file_valid = {
            "file": ("imagen.png", io.BytesIO(b"fake image data"), "image/png")
        }

        resp_upload_ok = await ac.post(
            f"/api/modules/blog/{SITE_ID}/upload-image",
            files=file_valid,
            headers=auth_headers,
        )

        assert resp_upload_ok.status_code == 200
        assert "url" in resp_upload_ok.json()

        file_invalid = {
            "file": ("virus.txt", io.BytesIO(b"hack"), "text/plain")
        }

        resp_upload_bad = await ac.post(
            f"/api/modules/blog/{SITE_ID}/upload-image",
            files=file_invalid,
            headers=auth_headers,
        )

        assert resp_upload_bad.status_code == 400


@pytest.mark.asyncio
async def test_blog_excepciones_y_modulo():
    """
    Cubre funciones del módulo y error 500 en upload-image.
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
        await ac.post(
            "/api/auth/registro",
            json={
                "correo": "blog500@test.com",
                "contrasena": "test123",
                "nombre": "Blog",
                "apellido": "Error",
            },
        )

        resp_login = await ac.post(
            "/api/auth/inicio",
            data={
                "username": "blog500@test.com",
                "password": "test123",
            },
        )

        token = resp_login.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        file_valid = {
            "file": ("imagen2.png", io.BytesIO(b"fake data"), "image/png")
        }

        with patch("builtins.open", side_effect=OSError("Disco lleno simulado")):
            resp_500 = await ac.post(
                f"/api/modules/blog/{SITE_ID}/upload-image",
                files=file_valid,
                headers=auth_headers,
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
        get_post_by_slug,
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
                status=PostStatus.PUBLISHED,
            ),
        )

        create_post(
            db,
            site_id,
            PostCreate(
                title="Post Programado Service",
                content="Contenido programado",
                status=PostStatus.SCHEDULED,
                published_at=datetime.now(timezone.utc) - timedelta(days=1),
            ),
        )

        create_post(
            db,
            site_id,
            PostCreate(
                title="Post Borrador Service",
                content="Contenido borrador",
                status=PostStatus.DRAFT,
            ),
        )

        publicados = get_posts_by_site(
            db,
            site_id,
            only_published=True,
        )

        slugs = [p.slug for p in publicados]

        assert post_publicado.slug in slugs
        assert any("post-programado-service" in slug for slug in slugs)
        assert not any("post-borrador-service" in slug for slug in slugs)

        post_encontrado = get_post_by_slug(
            db,
            site_id,
            post_publicado.slug,
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
    from datetime import datetime, timedelta, timezone
    from unittest.mock import MagicMock

    from app.packages.modulos.blog.routes import is_post_publicly_available

    post_scheduled_pasado = MagicMock()
    post_scheduled_pasado.is_deleted = False
    post_scheduled_pasado.status = "scheduled"
    post_scheduled_pasado.published_at = datetime.now(timezone.utc) - timedelta(days=1)

    assert is_post_publicly_available(post_scheduled_pasado) is True

    post_scheduled_futuro = MagicMock()
    post_scheduled_futuro.is_deleted = False
    post_scheduled_futuro.status = "scheduled"
    post_scheduled_futuro.published_at = datetime.now(timezone.utc) + timedelta(days=1)

    assert is_post_publicly_available(post_scheduled_futuro) is False

    post_published = MagicMock()
    post_published.is_deleted = False
    post_published.status = "published"
    post_published.published_at = None

    assert is_post_publicly_available(post_published) is True

    post_deleted = MagicMock()
    post_deleted.is_deleted = True
    post_deleted.status = "published"
    post_deleted.published_at = None

    assert is_post_publicly_available(post_deleted) is False

    post_draft = MagicMock()
    post_draft.is_deleted = False
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
    post.is_deleted = False

    result = MagicMock()
    result.scalar_one_or_none.return_value = post

    db = MagicMock()
    db.execute.return_value = result

    with patch(
        "app.packages.modulos.blog.routes.is_post_publicly_available",
        return_value=False,
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
        base_url="http://test",
    ) as ac:
        await ac.post(
            "/api/auth/registro",
            json={
                "correo": correo,
                "contrasena": "test123",
                "nombre": "Blog",
                "apellido": "Upload",
            },
        )

        resp_login = await ac.post(
            "/api/auth/inicio",
            data={
                "username": correo,
                "password": "test123",
            },
        )

        token = resp_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        archivo_sin_nombre = MagicMock()
        archivo_sin_nombre.content_type = "image/png"
        archivo_sin_nombre.filename = ""

        try:
            await upload_blog_image(
                site_id=1,
                file=archivo_sin_nombre,
                db=None,
                current_user=MagicMock(),
            )
            assert False
        except HTTPException as e:
            assert e.status_code == 400
            assert e.detail == "El archivo no tiene nombre válido"

        files_extension_mala = {
            "file": ("imagen.txt", io.BytesIO(b"fake data"), "image/png")
        }

        resp_extension_mala = await ac.post(
            "/api/modules/blog/1/upload-image",
            files=files_extension_mala,
            headers=headers,
        )

        assert resp_extension_mala.status_code == 400
        assert resp_extension_mala.json()["detail"] == "Extensión de imagen no permitida"

        files_vacio = {
            "file": ("imagen.png", io.BytesIO(b""), "image/png")
        }

        resp_vacio = await ac.post(
            "/api/modules/blog/1/upload-image",
            files=files_vacio,
            headers=headers,
        )

        assert resp_vacio.status_code == 400
        assert resp_vacio.json()["detail"] == "El archivo está vacío"


def test_blog_routes_list_categories_route(monkeypatch):
    from unittest.mock import MagicMock

    from app.packages.modulos.blog import routes

    db = MagicMock()
    expected_categories = [MagicMock()]

    def fake_get_categories_by_site(received_db, received_site_id):
        assert received_db is db
        assert received_site_id == 1
        return expected_categories

    monkeypatch.setattr(
        routes.services,
        "get_categories_by_site",
        fake_get_categories_by_site,
    )

    result = routes.list_categories_route(
        site_id=1,
        db=db,
    )

    assert result is expected_categories


def test_blog_routes_update_category_route(monkeypatch):
    from unittest.mock import MagicMock

    from app.packages.modulos.blog import routes

    db = MagicMock()
    category_in = MagicMock()
    expected_category = MagicMock()

    def fake_update_category(
        received_db,
        received_site_id,
        received_category_id,
        received_category_in,
    ):
        assert received_db is db
        assert received_site_id == 1
        assert received_category_id == 5
        assert received_category_in is category_in
        return expected_category

    monkeypatch.setattr(
        routes.services,
        "update_category",
        fake_update_category,
    )

    result = routes.update_category_route(
        site_id=1,
        category_id=5,
        category_in=category_in,
        db=db,
    )

    assert result is expected_category


def test_blog_routes_delete_category_route(monkeypatch):
    from unittest.mock import MagicMock

    from app.packages.modulos.blog import routes

    db = MagicMock()
    called = {}

    def fake_delete_category(received_db, received_site_id, received_category_id):
        called["ok"] = True
        assert received_db is db
        assert received_site_id == 1
        assert received_category_id == 5

    monkeypatch.setattr(
        routes.services,
        "delete_category",
        fake_delete_category,
    )

    result = routes.delete_category_route(
        site_id=1,
        category_id=5,
        db=db,
    )

    assert called["ok"] is True
    assert result == {"message": "Categoría eliminada correctamente"}


def test_blog_services_update_post_con_auditoria(db):
    from app.packages.modulos.blog import services
    from app.packages.modulos.blog.schemas import PostCreate, PostUpdate
    from app.models.auditoria import Auditoria

    site_id = 1

    post = services.create_post(
        db,
        site_id,
        PostCreate(
            title="Post original auditoria",
            content="Contenido original",
            status="draft",
        ),
        usuario_id=10,
    )

    updated = services.update_post(
        db,
        site_id,
        post.id,
        PostUpdate(
            title="Post actualizado auditoria",
            content="Contenido actualizado",
        ),
        usuario_id=20,
    )

    assert updated.id == post.id
    assert updated.title == "Post actualizado auditoria"
    assert updated.content == "Contenido actualizado"
    assert updated.slug.startswith("post-actualizado-auditoria")

    auditorias = (
        db.query(Auditoria)
        .filter(
            Auditoria.entidad == "blog_posts",
            Auditoria.entidad_id == post.id,
        )
        .all()
    )

    acciones = [audit.accion for audit in auditorias]

    assert "INSERT" in acciones
    assert "UPDATE" in acciones


def test_blog_services_delete_post_soft_delete_y_auditoria(db):
    from app.packages.modulos.blog import services
    from app.packages.modulos.blog.models import Post
    from app.packages.modulos.blog.schemas import PostCreate
    from app.models.auditoria import Auditoria

    site_id = 1

    post = services.create_post(
        db,
        site_id,
        PostCreate(
            title="Post para eliminar auditoria",
            content="Contenido",
            status="draft",
        ),
    )

    services.delete_post(
        db,
        site_id,
        post.id,
        usuario_id=30,
    )

    deleted_post = db.query(Post).filter(Post.id == post.id).first()

    assert deleted_post is not None
    assert deleted_post.is_deleted is True
    assert deleted_post.deleted_at is not None
    assert deleted_post.deleted_by == 30

    auditoria = (
        db.query(Auditoria)
        .filter(
            Auditoria.entidad == "blog_posts",
            Auditoria.entidad_id == post.id,
            Auditoria.accion == "DELETE",
        )
        .first()
    )

    assert auditoria is not None
    assert auditoria.usuario_id == 30


def test_blog_services_update_category_con_auditoria(db):
    from app.packages.modulos.blog import services
    from app.packages.modulos.blog.schemas import CategoryCreate
    from app.models.auditoria import Auditoria

    site_id = 1

    category = services.create_category(
        db,
        site_id,
        CategoryCreate(
            name="Categoría original auditoria",
            description="Descripción original",
        ),
        usuario_id=10,
    )

    updated = services.update_category(
        db,
        site_id,
        category.id,
        CategoryCreate(
            name="Categoría actualizada auditoria",
            description="Descripción actualizada",
        ),
        usuario_id=20,
    )

    assert updated.id == category.id
    assert updated.name == "Categoría actualizada auditoria"
    assert updated.description == "Descripción actualizada"
    assert updated.slug.startswith("categoria-actualizada-auditoria")

    auditorias = (
        db.query(Auditoria)
        .filter(
            Auditoria.entidad == "blog_categories",
            Auditoria.entidad_id == category.id,
        )
        .all()
    )

    acciones = [audit.accion for audit in auditorias]

    assert "INSERT" in acciones
    assert "UPDATE" in acciones


def test_blog_services_delete_category_soft_delete_y_auditoria(db):
    from app.packages.modulos.blog import services
    from app.packages.modulos.blog.models import Category
    from app.packages.modulos.blog.schemas import CategoryCreate
    from app.models.auditoria import Auditoria

    site_id = 1

    category = services.create_category(
        db,
        site_id,
        CategoryCreate(
            name="Categoría para eliminar auditoria",
            description="Descripción",
        ),
    )

    services.delete_category(
        db,
        site_id,
        category.id,
        usuario_id=30,
    )

    deleted_category = (
        db.query(Category)
        .filter(Category.id == category.id)
        .first()
    )

    assert deleted_category is not None
    assert deleted_category.is_deleted is True
    assert deleted_category.deleted_at is not None
    assert deleted_category.deleted_by == 30

    auditoria = (
        db.query(Auditoria)
        .filter(
            Auditoria.entidad == "blog_categories",
            Auditoria.entidad_id == category.id,
            Auditoria.accion == "DELETE",
        )
        .first()
    )

    assert auditoria is not None
    assert auditoria.usuario_id == 30


def test_blog_services_get_post_by_id_no_encontrado(db):
    from fastapi import HTTPException

    from app.packages.modulos.blog import services

    with pytest.raises(HTTPException) as exc:
        services.get_post_by_id(
            db,
            site_id=999,
            post_id=999,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Artículo no encontrado"


def test_blog_services_get_category_by_id_no_encontrada(db):
    from fastapi import HTTPException

    from app.packages.modulos.blog import services

    with pytest.raises(HTTPException) as exc:
        services.get_category_by_id(
            db,
            site_id=999,
            category_id=999,
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Categoría no encontrada"
def test_blog_services_generate_unique_category_slug_repetido(db):
    from app.packages.modulos.blog import services
    from app.packages.modulos.blog.schemas import CategoryCreate

    site_id = 1

    category_1 = services.create_category(
        db,
        site_id,
        CategoryCreate(
            name="Categoría repetida coverage",
            description="Primera categoría",
        ),
    )

    category_2 = services.create_category(
        db,
        site_id,
        CategoryCreate(
            name="Categoría repetida coverage",
            description="Segunda categoría",
        ),
    )

    assert category_1.slug == "categoria-repetida-coverage"
    assert category_2.slug == "categoria-repetida-coverage-1"


def test_blog_services_get_category_by_id_existente(db):
    from app.packages.modulos.blog import services
    from app.packages.modulos.blog.schemas import CategoryCreate

    site_id = 1

    category = services.create_category(
        db,
        site_id,
        CategoryCreate(
            name="Categoría buscar por id coverage",
            description="Categoría para cubrir get_category_by_id",
        ),
    )

    found = services.get_category_by_id(
        db,
        site_id,
        category.id,
    )

    assert found.id == category.id
    assert found.name == "Categoría buscar por id coverage"
    assert found.slug == "categoria-buscar-por-id-coverage"

def test_blog_services_get_categories_by_site(db):
    from app.packages.modulos.blog import services
    from app.packages.modulos.blog.schemas import CategoryCreate

    site_id = 1

    category_a = services.create_category(
        db,
        site_id,
        CategoryCreate(
            name="Categoria lista A coverage",
            description="Categoria A",
        ),
    )

    category_b = services.create_category(
        db,
        site_id,
        CategoryCreate(
            name="Categoria lista B coverage",
            description="Categoria B",
        ),
    )

    categories = services.get_categories_by_site(db, site_id)

    category_ids = [category.id for category in categories]

    assert category_a.id in category_ids
    assert category_b.id in category_ids
    assert all(category.site_id == site_id for category in categories)
    assert all(category.is_deleted is False for category in categories)