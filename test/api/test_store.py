import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock
import uuid
from sqlalchemy import text
from app import service
from app.main import app
from app.db.database import engine, get_db
from app.models.sitio import Sitio
from sqlalchemy.orm import Session as DBSession
from app.packages.modulos.store.schemas import CheckoutRequest
from app.packages.modulos.store import TiendaModule, module as tienda_mod_instance
from app.packages.modulos.store.schemas import CategoriaCreate, ProductoCreate
from app.packages.modulos.store.services import StoreService

BASE_URL = "http://test"
FAKE_SITE_ID = 1


def mock_sitio():
    """Retorna un mock de Sitio que siempre existe."""
    sitio = MagicMock()
    sitio.id = FAKE_SITE_ID
    return sitio


def get_db_override():
    """DB real para operaciones de store, pero con Sitio mockeado."""
    db = next(get_db())
    # Monkey-patch: cuando busque Sitio, siempre lo encuentra
    original_execute = db.execute

    def patched_execute(stmt, *args, **kwargs):
        # Si la query es sobre Sitio, devolver mock
        stmt_str = str(stmt)
        if "sitios" in stmt_str and "tienda" not in stmt_str:
            result = MagicMock()
            result.scalar_one_or_none.return_value = mock_sitio()
            return result
        return original_execute(stmt, *args, **kwargs)

    db.execute = patched_execute
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def override_db():
    app.dependency_overrides[get_db] = get_db_override

    with DBSession(engine) as db:
        db.execute(text("DELETE FROM tienda_items_pedido"))
        db.execute(text("DELETE FROM tienda_pedidos"))
        db.execute(text("DELETE FROM tienda_items_carrito"))
        db.execute(text("DELETE FROM tienda_carritos"))
        db.execute(text("DELETE FROM tienda_productos"))
        db.execute(text("DELETE FROM tienda_categorias"))

        db.execute(text("DELETE FROM usuarios_sitio WHERE id = 1 OR correo = 'store@test.com'"))

        db.execute(text("""
            INSERT INTO usuarios_sitio (
                id, id_sitio, correo, contrasena, nombre, apellido, activo
            )
            VALUES (
                1, 1, 'store@test.com', '123456', 'Store', 'User', true
            )
        """))

        db.commit()

    yield

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_store_flujo_completo():
    uid = uuid.uuid4().hex[:6]
    site_db_id = FAKE_SITE_ID

    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:

        resp_404_site = await ac.get("/api/v1/sitios/999999/tienda/productos")
        assert resp_404_site.status_code == 200  # con mock siempre encuentra el sitio

        cat_data = {"nombre": "Laptops", "slug": f"laptops-{uid}", "descripcion": "PCs"}
        resp_cat = await ac.post(f"/api/v1/sitios/{site_db_id}/tienda/categorias", json=cat_data)
        assert resp_cat.status_code == 201
        cat_id = resp_cat.json()["id"]

        resp_cat_get = await ac.get(f"/api/v1/sitios/{site_db_id}/tienda/categorias")
        assert resp_cat_get.status_code == 200

        resp_cat_one = await ac.get(f"/api/v1/sitios/{site_db_id}/tienda/categorias/{cat_id}")
        assert resp_cat_one.status_code == 200

        resp_cat_upd = await ac.put(f"/api/v1/sitios/{site_db_id}/tienda/categorias/{cat_id}", json={"nombre": "Laptops Gamer"})
        assert resp_cat_upd.status_code == 200

        await ac.get(f"/api/v1/sitios/{site_db_id}/tienda/categorias/999999")
        await ac.put(f"/api/v1/sitios/{site_db_id}/tienda/categorias/999999", json={"nombre": "No"})
        await ac.delete(f"/api/v1/sitios/{site_db_id}/tienda/categorias/999999")

        prod_data_1 = {"nombre": "Laptop X", "slug": f"laptop-x-{uid}", "precio": 1000.0, "stock": 10, "categoria_id": cat_id}
        resp_prod_1 = await ac.post(f"/api/v1/sitios/{site_db_id}/tienda/productos", json=prod_data_1)
        assert resp_prod_1.status_code == 201
        prod_id_1 = resp_prod_1.json()["id"]

        prod_data_2 = {"nombre": "Laptop Y", "slug": f"laptop-y-{uid}", "precio": 500.0, "stock": 2, "es_activo": True}
        resp_prod_2 = await ac.post(f"/api/v1/sitios/{site_db_id}/tienda/productos", json=prod_data_2)
        assert resp_prod_2.status_code == 201
        prod_id_2 = resp_prod_2.json()["id"]

        await ac.get(f"/api/v1/sitios/{site_db_id}/tienda/productos?featured=true")

        resp_prod_one = await ac.get(f"/api/v1/sitios/{site_db_id}/tienda/productos/{prod_id_1}")
        assert resp_prod_one.status_code == 200

        resp_prod_upd = await ac.put(f"/api/v1/sitios/{site_db_id}/tienda/productos/{prod_id_1}", json={"precio": 1200.0})
        assert resp_prod_upd.status_code == 200

        await ac.get(f"/api/v1/sitios/{site_db_id}/tienda/productos/999999")
        await ac.put(f"/api/v1/sitios/{site_db_id}/tienda/productos/999999", json={"precio": 1})
        await ac.delete(f"/api/v1/sitios/{site_db_id}/tienda/productos/999999")

        resp_cart_empty = await ac.get(f"/api/v1/sitios/{site_db_id}/tienda/carrito")
        assert resp_cart_empty.json()["id"] == 0

        resp_cart_bad = await ac.post(f"/api/v1/sitios/{site_db_id}/tienda/carrito/items", json={"producto_id": prod_id_1, "cantidad": 1})
        assert resp_cart_bad.status_code == 401

        item_data = {"producto_id": prod_id_1, "cantidad": 2, "usuario_id": 1}
        resp_item = await ac.post(f"/api/v1/sitios/{site_db_id}/tienda/carrito/items", json=item_data)
        assert resp_item.status_code == 200
        item_id = resp_item.json()["id"]

        # Cubrir DELETE exitoso de item carrito -> routes.py línea 467
        resp_item_temp = await ac.post(
            f"/api/v1/sitios/{site_db_id}/tienda/carrito/items",
            json={
                "producto_id": prod_id_2,
                "cantidad": 1,
                "usuario_id": 1
            }
        )
        assert resp_item_temp.status_code == 200
        item_temp_id = resp_item_temp.json()["id"]

        resp_delete_ok = await ac.delete(
            f"/api/v1/sitios/{site_db_id}/tienda/carrito/items/{item_temp_id}"
        )
        assert resp_delete_ok.status_code == 204


        resp_cart_user = await ac.get(
        f"/api/v1/sitios/{site_db_id}/tienda/carrito?usuario_id=1"
        )
        assert resp_cart_user.status_code == 200
        assert resp_cart_user.json()["id"] != 0
        assert len(resp_cart_user.json()["items"]) >= 1

        await ac.post(f"/api/v1/sitios/{site_db_id}/tienda/carrito/items", json={"producto_id": prod_id_1, "cantidad": 1, "usuario_id": 1})

        resp_stock_bad = await ac.post(f"/api/v1/sitios/{site_db_id}/tienda/carrito/items", json={"producto_id": prod_id_1, "cantidad": 20, "usuario_id": 1})
        assert resp_stock_bad.status_code == 400

        resp_item_upd = await ac.put(f"/api/v1/sitios/{site_db_id}/tienda/carrito/items/{item_id}", params={"cantidad": 4})
        assert resp_item_upd.status_code == 200

        await ac.put(f"/api/v1/sitios/{site_db_id}/tienda/carrito/items/999999", params={"cantidad": 1})
        await ac.delete(f"/api/v1/sitios/{site_db_id}/tienda/carrito/items/999999")

        resp_item_del_0 = await ac.put(f"/api/v1/sitios/{site_db_id}/tienda/carrito/items/{item_id}", params={"cantidad": 0})
        assert resp_item_del_0.status_code == 404

        await ac.post(f"/api/v1/sitios/{site_db_id}/tienda/carrito/items", json={"producto_id": prod_id_1, "cantidad": 1, "usuario_id": 1})

        checkout_data = {"nombre_cliente": "Juan", "email_cliente": "j@j.com", "usuario_id": 1}

        resp_checkout = await ac.post(f"/api/v1/sitios/{site_db_id}/tienda/checkout", json=checkout_data)
        assert resp_checkout.status_code == 200
        pedido_id = resp_checkout.json()["pedido"]["id"]

        resp_checkout_empty = await ac.post(f"/api/v1/sitios/{site_db_id}/tienda/checkout", json=checkout_data)
        assert resp_checkout_empty.status_code == 400

        resp_pedidos = await ac.get(f"/api/v1/sitios/{site_db_id}/tienda/pedidos")
        assert resp_pedidos.status_code == 200

        resp_pedido_one = await ac.get(f"/api/v1/sitios/{site_db_id}/tienda/pedidos/{pedido_id}")
        assert resp_pedido_one.status_code == 200

        resp_pedido_upd = await ac.put(f"/api/v1/sitios/{site_db_id}/tienda/pedidos/{pedido_id}/estado", json={"estado": "procesando"})
        assert resp_pedido_upd.status_code == 200

        resp_pedido_bad_state = await ac.put(f"/api/v1/sitios/{site_db_id}/tienda/pedidos/{pedido_id}/estado", json={"estado": "estado-inventado"})
        assert resp_pedido_bad_state.status_code == 400

        await ac.get(f"/api/v1/sitios/{site_db_id}/tienda/pedidos/999999")
        await ac.put(f"/api/v1/sitios/{site_db_id}/tienda/pedidos/999999/estado", json={"estado": "pendiente"})

        await ac.post(f"/api/v1/sitios/{site_db_id}/tienda/carrito/items", json={"producto_id": prod_id_2, "cantidad": 2, "usuario_id": 1})
        await ac.put(f"/api/v1/sitios/{site_db_id}/tienda/productos/{prod_id_2}", json={"stock": 1})

        resp_checkout_fail = await ac.post(f"/api/v1/sitios/{site_db_id}/tienda/checkout", json=checkout_data)
        assert resp_checkout_fail.status_code == 400

        await ac.delete(f"/api/v1/sitios/{site_db_id}/tienda/categorias/{cat_id}")
        await ac.delete(f"/api/v1/sitios/{site_db_id}/tienda/productos/{prod_id_1}")


@pytest.mark.asyncio
async def test_store_excepciones_y_modulo():
    tienda_mod = TiendaModule()
    assert len(tienda_mod.get_models()) > 0
    assert len(tienda_mod.get_schemas()) > 0
    assert len(tienda_mod.get_admin_menu()) > 0
    tienda_mod.on_activate(1, None, {})
    tienda_mod.on_deactivate(1, None)
    tienda_mod.on_install(None)

    site_db_id = FAKE_SITE_ID

    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        with DBSession(engine) as db:
            service = StoreService(db, site_db_id)

            service.obtener_o_crear_carrito(usuario_id=1)
            carrito_leido = service.obtener_carrito(usuario_id=1)
            assert carrito_leido.usuario_id == 1

            try:
                service.agregar_al_carrito(producto_id=999999, cantidad=1, usuario_id=1)
            except ValueError:
                pass

        # El mock de Session.execute para carrito ya no aplica igual con override
        # pero sí el de services
        with patch("app.packages.modulos.store.services.StoreService.agregar_al_carrito", side_effect=Exception("DB Error")):
            resp = await ac.post(f"/api/v1/sitios/{site_db_id}/tienda/carrito/items", json={"producto_id": 1, "cantidad": 1, "usuario_id": 1})
            assert resp.status_code == 500

        with patch("app.packages.modulos.store.services.StoreService.crear_pedido", side_effect=Exception("DB Error")):
            resp = await ac.post(f"/api/v1/sitios/{site_db_id}/tienda/checkout", json={"nombre_cliente": "Juan", "email_cliente": "j@j.com", "usuario_id": 1})
            assert resp.status_code == 500

        # Forzar error en carrito (exception en el try/except del route)
        with patch("app.packages.modulos.store.routes.StoreService", side_effect=Exception("DB Error")):
            resp = await ac.get(f"/api/v1/sitios/{site_db_id}/tienda/carrito?usuario_id=1")
            assert resp.status_code == 200
            assert "id" in resp.json()

@pytest.mark.asyncio
async def test_store_services_lineas_faltantes():

    with DBSession(engine) as db:

        service = StoreService(db, FAKE_SITE_ID)

        carrito = service.obtener_o_crear_carrito(usuario_id=1)
        assert carrito.usuario_id == 1

        try:
            service.agregar_al_carrito(
                producto_id=999999,
                cantidad=999
            )
        except ValueError:
            pass

        categoria = service.crear_categoria(
            CategoriaCreate(
                nombre="Test",
                slug="test-slug"
            )
        )

        producto = service.crear_producto(
            ProductoCreate(
                nombre="Producto Test",
                slug="producto-test",
                precio=10,
                stock=1,
                categoria_id=categoria.id,
                es_featured=True
            )
        )

        # Cubre filtro por categoria_id en listar_productos
        productos_categoria, total_categoria = service.listar_productos(
            categoria_id=categoria.id
        )
        assert total_categoria >= 1
        assert len(productos_categoria) >= 1

        item = service.agregar_al_carrito(
        producto_id=producto.id,
        cantidad=1,
        usuario_id=1
        )

        assert item.id is not None

        # Cubre stock insuficiente cuando el item ya existe en carrito
        try:
            service.agregar_al_carrito(
                producto_id=producto.id,
                cantidad=1,
                usuario_id=1
            )
        except ValueError:
            pass

        pedido = service.crear_pedido(
            CheckoutRequest(
                nombre_cliente="Juan",
                email_cliente="j@j.com"
            ),
            usuario_id=1
        )

        assert pedido.estado == "pendiente"

        # Cubre filtro por estado en listar_pedidos
        pedidos_estado, total_estado = service.listar_pedidos(
            estado="pendiente"
        )
        assert total_estado >= 1
        assert len(pedidos_estado) >= 1

        try:
            service.actualizar_estado_pedido(
                pedido.id,
                "estado-falso"
            )
        except ValueError:
            pass

        pedido_actualizado = service.actualizar_estado_pedido(
            pedido.id,
            "procesando"
        )

        assert pedido_actualizado.estado == "procesando"

        # Cubre eliminar_del_carrito cuando SÍ existe el item
        producto_2 = service.crear_producto(
            ProductoCreate(
                nombre="Producto Eliminar",
                slug="producto-eliminar",
                precio=20,
                stock=5,
                categoria_id=categoria.id
            )
        )

        item_eliminar = service.agregar_al_carrito(
            producto_id=producto_2.id,
            cantidad=1,
            usuario_id=1
        )

        eliminado = service.eliminar_del_carrito(item_eliminar.id)
        assert eliminado is True

        # Cubre obtener_carrito por usuario_id
        carrito_usuario = service.obtener_carrito(usuario_id=1)
        assert carrito_usuario is not None

@pytest.mark.asyncio
async def test_store_routes_sitio_no_encontrado():

    def get_db_real():
        db = next(get_db())
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = get_db_real

    site_bad = 999999999

    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:

        resp = await ac.get(f"/api/v1/sitios/{site_bad}/tienda/productos")
        assert resp.status_code == 404

        resp = await ac.post(
            f"/api/v1/sitios/{site_bad}/tienda/productos",
            json={
                "nombre": "Producto X",
                "slug": "producto-x",
                "precio": 10,
                "stock": 1
            }
        )
        assert resp.status_code == 404

        resp = await ac.get(f"/api/v1/sitios/{site_bad}/tienda/productos/1")
        assert resp.status_code == 404

        resp = await ac.put(
            f"/api/v1/sitios/{site_bad}/tienda/productos/1",
            json={"precio": 99}
        )
        assert resp.status_code == 404

        resp = await ac.delete(f"/api/v1/sitios/{site_bad}/tienda/productos/1")
        assert resp.status_code == 404

        resp = await ac.get(f"/api/v1/sitios/{site_bad}/tienda/categorias")
        assert resp.status_code == 404

        resp = await ac.post(
            f"/api/v1/sitios/{site_bad}/tienda/categorias",
            json={
                "nombre": "Categoria X",
                "slug": "categoria-x"
            }
        )
        assert resp.status_code == 404

        resp = await ac.get(f"/api/v1/sitios/{site_bad}/tienda/categorias/1")
        assert resp.status_code == 404

        resp = await ac.put(
            f"/api/v1/sitios/{site_bad}/tienda/categorias/1",
            json={"nombre": "Nueva Categoria"}
        )
        assert resp.status_code == 404

        resp = await ac.delete(f"/api/v1/sitios/{site_bad}/tienda/categorias/1")
        assert resp.status_code == 404

        resp = await ac.get(f"/api/v1/sitios/{site_bad}/tienda/pedidos")
        assert resp.status_code == 404

        resp = await ac.get(f"/api/v1/sitios/{site_bad}/tienda/pedidos/1")
        assert resp.status_code == 404

        resp = await ac.put(
            f"/api/v1/sitios/{site_bad}/tienda/pedidos/1/estado",
            json={"estado": "pendiente"}
        )
        assert resp.status_code == 404

        resp = await ac.get(f"/api/v1/sitios/{site_bad}/tienda/carrito?usuario_id=1")
        assert resp.status_code == 200
        assert "id" in resp.json()

        resp = await ac.post(
            f"/api/v1/sitios/{site_bad}/tienda/carrito/items",
            json={
                "producto_id": 1,
                "cantidad": 1,
                "usuario_id": 1
            }
        )
        assert resp.status_code == 404

        resp = await ac.put(
            f"/api/v1/sitios/{site_bad}/tienda/carrito/items/1",
            params={"cantidad": 1}
        )
        assert resp.status_code == 404

        resp = await ac.delete(f"/api/v1/sitios/{site_bad}/tienda/carrito/items/1")
        assert resp.status_code == 404

        resp = await ac.post(
            f"/api/v1/sitios/{site_bad}/tienda/checkout",
            json={
                "nombre_cliente": "Juan",
                "email_cliente": "j@j.com",
                "usuario_id": 1
            }
        )
        assert resp.status_code == 404

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_store_services_checkout_producto_inactivo():

    with DBSession(engine) as db:

        service = StoreService(db, FAKE_SITE_ID)

        categoria = service.crear_categoria(
            CategoriaCreate(
                nombre="Categoria Inactiva",
                slug="categoria-inactiva"
            )
        )

        producto = service.crear_producto(
            ProductoCreate(
                nombre="Producto Inactivo",
                slug="producto-inactivo",
                precio=10,
                stock=5,
                categoria_id=categoria.id
            )
        )

        item_eliminar = service.agregar_al_carrito(
            producto_id=producto.id,
            cantidad=1,
            usuario_id=1
        )

        assert item_eliminar.id is not None

        producto.es_activo = False
        db.commit()

        try:
            service.crear_pedido(
                CheckoutRequest(
                    nombre_cliente="Juan",
                    email_cliente="j@j.com"
                ),
                usuario_id=1
            )
            assert False
        except ValueError as e:
            assert "No hay productos válidos" in str(e)


@pytest.mark.asyncio
async def test_store_services_crear_pedido_sin_usuario():
    with DBSession(engine) as db:
        service = StoreService(db, FAKE_SITE_ID)

        try:
            service.crear_pedido(
                CheckoutRequest(
                    nombre_cliente="Juan",
                    email_cliente="j@j.com"
                ),
                usuario_id=None
            )
            assert False
        except ValueError as e:
            assert "Debes iniciar sesión para finalizar la compra" in str(e)

@pytest.mark.asyncio
async def test_store_routes_carrito_producto_inactivo():
    with DBSession(engine) as db:
        service = StoreService(db, FAKE_SITE_ID)

        categoria = service.crear_categoria(
            CategoriaCreate(
                nombre="Categoria Carrito Inactivo",
                slug="categoria-carrito-inactivo"
            )
        )

        producto = service.crear_producto(
            ProductoCreate(
                nombre="Producto Carrito Inactivo",
                slug="producto-carrito-inactivo",
                precio=10,
                stock=5,
                categoria_id=categoria.id
            )
        )

        item = service.agregar_al_carrito(
            producto_id=producto.id,
            cantidad=1,
            usuario_id=1
        )

        assert item.id is not None

        producto.es_activo = False
        db.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        resp = await ac.get(
            f"/api/v1/sitios/{FAKE_SITE_ID}/tienda/carrito?usuario_id=1"
        )

        assert resp.status_code == 200
        assert resp.json()["id"] != 0
        assert resp.json()["items"] == []
        assert resp.json()["total"] == 0

@pytest.mark.asyncio
async def test_store_routes_checkout_sin_usuario():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        resp = await ac.post(
            f"/api/v1/sitios/{FAKE_SITE_ID}/tienda/checkout",
            json={
                "nombre_cliente": "Juan",
                "email_cliente": "j@j.com"
            }
        )

        assert resp.status_code == 400
        assert resp.json()["detail"] == "Debes iniciar sesión para finalizar la compra"


@pytest.mark.asyncio
async def test_store_routes_upload_image_validaciones_y_ok():
    import io
    from unittest.mock import MagicMock
    from fastapi import HTTPException

    from app.packages.modulos.store.routes import upload_tienda_image

    async with AsyncClient(transport=ASGITransport(app=app), base_url=BASE_URL) as ac:
        # Content type inválido
        resp_tipo_malo = await ac.post(
            f"/api/v1/sitios/{FAKE_SITE_ID}/tienda/upload-image",
            files={
                "file": ("archivo.txt", io.BytesIO(b"fake"), "text/plain")
            }
        )

        assert resp_tipo_malo.status_code == 400
        assert resp_tipo_malo.json()["detail"] == "Solo se permiten imágenes JPG, PNG, WEBP o GIF"

        # Extensión inválida aunque content_type sea imagen
        resp_ext_mala = await ac.post(
            f"/api/v1/sitios/{FAKE_SITE_ID}/tienda/upload-image",
            files={
                "file": ("archivo.txt", io.BytesIO(b"fake"), "image/png")
            }
        )

        assert resp_ext_mala.status_code == 400
        assert resp_ext_mala.json()["detail"] == "Extensión de imagen no permitida"

        # Archivo vacío
        resp_vacio = await ac.post(
            f"/api/v1/sitios/{FAKE_SITE_ID}/tienda/upload-image",
            files={
                "file": ("imagen.png", io.BytesIO(b""), "image/png")
            }
        )

        assert resp_vacio.status_code == 400
        assert resp_vacio.json()["detail"] == "El archivo está vacío"

        # Upload correcto
        resp_ok = await ac.post(
            f"/api/v1/sitios/{FAKE_SITE_ID}/tienda/upload-image",
            files={
                "file": ("imagen.png", io.BytesIO(b"fake image data"), "image/png")
            }
        )

        assert resp_ok.status_code == 200
        assert resp_ok.json()["url"].startswith("/uploads/tienda/")

    # Filename vacío: FastAPI suele devolver 422, por eso se cubre directo
    archivo_sin_nombre = MagicMock()
    archivo_sin_nombre.content_type = "image/png"
    archivo_sin_nombre.filename = ""

    try:
        await upload_tienda_image(file=archivo_sin_nombre)
        assert False
    except HTTPException as e:
        assert e.status_code == 400
        assert e.detail == "El archivo no tiene nombre válido"

    from unittest.mock import AsyncMock

    # Error OSError al escribir archivo
    archivo_error = MagicMock()
    archivo_error.content_type = "image/png"
    archivo_error.filename = "imagen.png"
    archivo_error.read = AsyncMock(return_value=b"fake image data")

    with patch("builtins.open", side_effect=OSError("Disco lleno tienda")):
        try:
            await upload_tienda_image(file=archivo_error)
            assert False
        except HTTPException as e:
            assert e.status_code == 500
            assert "Disco lleno tienda" in e.detail

def test_store_routes_obtener_carrito_producto_inactivo_directo():
    from unittest.mock import MagicMock
    from app.packages.modulos.store.routes import obtener_carrito

    sitio = MagicMock()
    sitio.id = FAKE_SITE_ID

    carrito = MagicMock()
    carrito.id = 1
    carrito.site_id = FAKE_SITE_ID
    carrito.usuario_id = 1

    item = MagicMock()
    item.id = 10
    item.producto_id = 999
    item.cantidad = 2

    result_sitio = MagicMock()
    result_sitio.scalar_one_or_none.return_value = sitio

    result_carrito = MagicMock()
    result_carrito.scalar_one_or_none.return_value = carrito

    result_items = MagicMock()
    result_items.scalars.return_value.all.return_value = [item]

    result_producto_inactivo = MagicMock()
    result_producto_inactivo.scalar_one_or_none.return_value = None

    db = MagicMock()
    db.execute.side_effect = [
        result_sitio,
        result_carrito,
        result_items,
        result_producto_inactivo
    ]

    response = obtener_carrito(
        sitio_id=FAKE_SITE_ID,
        usuario_id=1,
        db=db
    )

    assert response.id == carrito.id
    assert response.site_id == FAKE_SITE_ID
    assert response.items == []
    assert response.total == 0



def test_store_routes_obtener_carrito_usuario_sin_carrito_directo():
    from unittest.mock import MagicMock
    from app.packages.modulos.store.routes import obtener_carrito

    sitio = MagicMock()
    sitio.id = FAKE_SITE_ID

    result_sitio = MagicMock()
    result_sitio.scalar_one_or_none.return_value = sitio

    result_carrito_vacio = MagicMock()
    result_carrito_vacio.scalar_one_or_none.return_value = None

    db = MagicMock()
    db.execute.side_effect = [
        result_sitio,
        result_carrito_vacio
    ]

    response = obtener_carrito(
        sitio_id=FAKE_SITE_ID,
        usuario_id=999,
        db=db
    )

    assert response.id == 0
    assert response.site_id == FAKE_SITE_ID
    assert response.items == []
    assert response.total == 0

