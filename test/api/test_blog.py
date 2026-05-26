import pytest
import io
from httpx import AsyncClient, ASGITransport
from app.main import app
from unittest.mock import patch # <-- Nueva importación para simular errores
from app.packages.modulos.blog import blog_module # <-- Importamos el módulo directamente
# Configuración base
BASE_URL = "http://test"
SITE_ID = 1

@pytest.mark.asyncio
async def test_blog_flujo_completo():
    """
    Prueba de integración completa del módulo Blog.
    Diseñada para alcanzar el 100% de coverage en routes.py y services.py
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        
        # ---------------------------------------------------------
        # 1. PREPARACIÓN: Crear un sitio temporal (Por si la BD está vacía)
        # Ignoramos si falla (significa que el sitio 1 ya existe)
        # ---------------------------------------------------------
        await ac.post("/api/sitios", json={"nombre": "Sitio Blog", "slug": "sitio-blog"})

        # ---------------------------------------------------------
        # 2. PROBAR CATEGORÍAS Y GENERADOR DE SLUGS
        # ---------------------------------------------------------
        cat_data = {"name": "Tecnología y Programación!", "description": "Tech"}
        resp_cat = await ac.post(f"/modules/blog/{SITE_ID}/categories", json=cat_data)
        assert resp_cat.status_code == 200
        # Validamos que limpió las tildes y caracteres especiales
        assert resp_cat.json()["slug"] == "tecnologia-y-programacion"

        # ---------------------------------------------------------
        # 3. PROBAR CREACIÓN DE POSTS Y SLUGS DUPLICADOS
        # ---------------------------------------------------------
        post_data_1 = {
            "title": "Mi Primer Post",
            "content": "Contenido 1"
        }
        resp_post_1 = await ac.post(f"/modules/blog/{SITE_ID}/posts", json=post_data_1)
        assert resp_post_1.status_code == 200
        post_1 = resp_post_1.json()
        assert post_1["slug"] == "mi-primer-post"

        # Creamos otro con el MISMO título para forzar el bucle `while True` del slug
        resp_post_2 = await ac.post(f"/modules/blog/{SITE_ID}/posts", json=post_data_1)
        assert resp_post_2.status_code == 200
        post_2 = resp_post_2.json()
        assert post_2["slug"] == "mi-primer-post-1"  # ¡Coverage del contador de slugs!

        # ---------------------------------------------------------
        # 4. PUBLICAR POST 1 (para poder consultarlo por slug)
        # ---------------------------------------------------------
        resp_upd_1 = await ac.put(
            f"/modules/blog/{SITE_ID}/posts/{post_1['id']}", 
            json={"status": "published"}
        )
        assert resp_upd_1.status_code == 200

        # Actualizar post 2 a PROGRAMADO en el PASADO (debería mostrarse como publicado)
        resp_upd_2 = await ac.put(
            f"/modules/blog/{SITE_ID}/posts/{post_2['id']}", 
            json={"status": "scheduled", "published_at": "2020-01-01T12:00:00Z"}
        )
        assert resp_upd_2.status_code == 200

        # ---------------------------------------------------------
        # 5. PROBAR GET POST BY SLUG Y ERRORES 404
        # ---------------------------------------------------------
        resp_get = await ac.get(f"/modules/blog/{SITE_ID}/posts/mi-primer-post")
        assert resp_get.status_code == 200
        assert resp_get.json()["id"] == post_1["id"]

        resp_get_404 = await ac.get(f"/modules/blog/{SITE_ID}/posts/slug-inventado")
        assert resp_get_404.status_code == 404

        # ---------------------------------------------------------
        # 6. PROBAR ACTUALIZACIÓN
        # ---------------------------------------------------------
        # Actualizar post inexistente (Coverage 404)
        resp_upd_404 = await ac.put(f"/modules/blog/{SITE_ID}/posts/9999", json={"title": "No"})
        assert resp_upd_404.status_code == 404

        # ---------------------------------------------------------
        # 7. PROBAR LISTADO Y FILTRO `only_published`
        # ---------------------------------------------------------
        # Traer todos
        resp_list_all = await ac.get(f"/modules/blog/{SITE_ID}/posts")
        assert resp_list_all.status_code == 200
        assert len(resp_list_all.json()) >= 2

        # Traer solo publicados (debe traer el 'published' y el 'scheduled' antiguo)
        resp_list_pub = await ac.get(f"/modules/blog/{SITE_ID}/posts?only_published=true")
        assert resp_list_pub.status_code == 200
        publicados = [p["id"] for p in resp_list_pub.json()]
        assert post_1["id"] in publicados
        assert post_2["id"] in publicados

        # ---------------------------------------------------------
        # 8. PROBAR ELIMINACIÓN DE POSTS
        # ---------------------------------------------------------
        resp_del = await ac.delete(f"/modules/blog/{SITE_ID}/posts/{post_2['id']}")
        assert resp_del.status_code == 200

        resp_del_404 = await ac.delete(f"/modules/blog/{SITE_ID}/posts/9999")
        assert resp_del_404.status_code == 404

        # ---------------------------------------------------------
        # 9. PREPARAR AUTH PARA SUBIDA DE IMÁGENES
        # ---------------------------------------------------------
        await ac.post("/api/auth/registro", json={
            "correo": "blog@test.com", "contrasena": "test123",
            "nombre": "Blog", "apellido": "Tester"
        })
        resp_login = await ac.post("/api/auth/inicio", data={
            "username": "blog@test.com", "password": "test123"
        })
        token = resp_login.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        # ---------------------------------------------------------
        # 10. PROBAR SUBIDA DE IMÁGENES (UPLOAD SEGURO)
        # ---------------------------------------------------------
        # Archivo válido (.png)
        file_valid = {"file": ("imagen.png", io.BytesIO(b"fake image data"), "image/png")}
        resp_upload_ok = await ac.post(f"/modules/blog/{SITE_ID}/upload-image", files=file_valid, headers=auth_headers)
        assert resp_upload_ok.status_code == 200
        assert "url" in resp_upload_ok.json()

        # Archivo inválido (.txt)
        file_invalid = {"file": ("virus.txt", io.BytesIO(b"hack"), "text/plain")}
        resp_upload_bad = await ac.post(f"/modules/blog/{SITE_ID}/upload-image", files=file_invalid, headers=auth_headers)
        assert resp_upload_bad.status_code == 400

@pytest.mark.asyncio
async def test_blog_excepciones_y_modulo():
    """
    Prueba diseñada para cubrir los casos borde faltantes y alcanzar el 100%.
    Cubre: __init__.py, module.py y el Error 500 en upload-image de routes.py.
    """
    # ---------------------------------------------------------
    # 1. CUBRIR __init__.py y module.py
    # ---------------------------------------------------------
    # Llamamos a los métodos de configuración del módulo
    modelos = blog_module.get_models()
    assert len(modelos) > 0
    
    esquemas = blog_module.get_schemas()
    assert len(esquemas) > 0

    # Llamamos a los métodos vacíos (interfaces) para que el lector pase por ellos
    blog_module.on_activate(site_id=1, db=None, config={})
    blog_module.on_deactivate(site_id=1, db=None)
    blog_module.on_install(db=None)
    menu = blog_module.get_admin_menu()
    assert isinstance(menu, list)

    # ---------------------------------------------------------
    # 2. CUBRIR routes.py (Líneas 118-119) - Error 500
    # ---------------------------------------------------------
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        # Registrar e iniciar sesión para obtener token
        await ac.post("/api/auth/registro", json={
            "correo": "blog500@test.com", "contrasena": "test123",
            "nombre": "Blog", "apellido": "Error"
        })
        resp_login = await ac.post("/api/auth/inicio", data={
            "username": "blog500@test.com", "password": "test123"
        })
        token = resp_login.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}

        file_valid = {"file": ("imagen2.png", io.BytesIO(b"fake data"), "image/png")}
        
        with patch("builtins.open", side_effect=OSError("Disco lleno simulado")):
            resp_500 = await ac.post(f"/modules/blog/{SITE_ID}/upload-image", files=file_valid, headers=auth_headers)
            
            assert resp_500.status_code == 500
            assert "Disco lleno simulado" in resp_500.json()["detail"]