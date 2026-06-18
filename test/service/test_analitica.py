import pytest
from datetime import datetime, timedelta, timezone

from app.packages.modulos.analitica import services
from app.packages.modulos.analitica.models import Visita, Evento, Sesion
from app.packages.modulos.analitica.schemas import VisitaCreate, EventoCreate


SITE_ID = 1


def _crear_sitio_con_modulos(db):
    from app.models.sitio import Sitio
    from app.models.modulo import Modulo

    blog_mod = Modulo(nombre="Blog", slug="blog", tipo="contenido", activo=True)
    tienda_mod = Modulo(nombre="Tienda", slug="tienda", tipo="comercio", activo=True)
    db.add_all([blog_mod, tienda_mod])
    db.flush()

    sitio = Sitio(nombre="Test", slug="test-site", activo=True)
    sitio.modulos = [blog_mod, tienda_mod]
    db.add(sitio)
    db.commit()
    db.refresh(sitio)
    return sitio


class TestRegistrarVisita:
    def test_registrar_visita(self, db):
        data = VisitaCreate(url="/test", titulo_pagina="Test", referer="https://google.com", session_id=None)
        visita = services.registrar_visita(db, SITE_ID, data, ip="192.168.1.1", user_agent="Mozilla/5.0 Chrome/120")
        assert visita.id is not None
        assert visita.url == "/test"
        assert visita.titulo_pagina == "Test"
        assert visita.referer == "https://google.com"
        assert visita.ip == "192.168.1.1"
        assert visita.navegador == "Chrome"
        assert visita.dispositivo == "Desktop"

    def test_registrar_visita_con_session_crea_sesion(self, db):
        data = VisitaCreate(url="/page", session_id="sess-001")
        services.registrar_visita(db, SITE_ID, data, ip="1.2.3.4", user_agent="Mozilla/5.0")
        sesion = db.query(Sesion).filter(Sesion.session_id == "sess-001").first()
        assert sesion is not None
        assert sesion.paginas_vistas == 1

    def test_registrar_visita_session_existente_actualiza(self, db):
        ahora = datetime.now(timezone.utc)
        sesion = Sesion(
            site_id=SITE_ID, session_id="sess-002",
            ip=None, user_agent=None,
            inicio=ahora - timedelta(minutes=5),
            fin=ahora - timedelta(minutes=5),
            paginas_vistas=1, duracion_segundos=300,
        )
        db.add(sesion)
        db.commit()

        data = VisitaCreate(url="/page2", session_id="sess-002")
        services.registrar_visita(db, SITE_ID, data, ip="1.2.3.4", user_agent="Mozilla/5.0")
        db.refresh(sesion)
        assert sesion.paginas_vistas == 2


class TestRegistrarEvento:
    def test_registrar_evento(self, db):
        data = EventoCreate(tipo="click", etiqueta="btn_compra", valor="50", url="/checkout", session_id="sess-001")
        evento = services.registrar_evento(db, SITE_ID, data)
        assert evento.id is not None
        assert evento.tipo == "click"
        assert evento.url == "/checkout"

    def test_registrar_evento_con_metadata(self, db):
        data = EventoCreate(tipo="pago", metadata_json={"monto": 100, "moneda": "USD"})
        evento = services.registrar_evento(db, SITE_ID, data)
        assert evento.metadata_json is not None


class TestDashboard:
    def test_obtener_dashboard_vacio(self, db):
        dashboard = services.obtener_dashboard(db, SITE_ID, dias=7)
        assert dashboard.resumen.visitas_hoy == 0
        assert dashboard.resumen.total_visitas == 0
        assert dashboard.resumen.total_eventos == 0
        assert dashboard.resumen.bounce_rate == 0.0
        assert dashboard.blog is None
        assert dashboard.tienda is None

    def test_obtener_dashboard_con_datos(self, db):
        ahora = datetime.now(timezone.utc)
        for i in range(5):
            v = Visita(site_id=SITE_ID, url=f"/page{i}", created_at=ahora - timedelta(hours=i))
            db.add(v)
        db.add(Evento(site_id=SITE_ID, tipo="click", session_id="s-1", created_at=ahora))
        db.add(Sesion(site_id=SITE_ID, session_id="s-1", paginas_vistas=1, inicio=ahora, fin=ahora, duracion_segundos=10))
        db.add(Sesion(site_id=SITE_ID, session_id="s-2", paginas_vistas=3, inicio=ahora, fin=ahora, duracion_segundos=30))
        db.commit()

        dashboard = services.obtener_dashboard(db, SITE_ID, dias=7)
        assert dashboard.resumen.visitas_hoy >= 5
        assert dashboard.resumen.total_visitas >= 5
        assert dashboard.resumen.visitantes_unicos >= 0
        assert dashboard.resumen.bounce_rate > 0
        assert len(dashboard.ultimas_visitas) >= 1
        assert len(dashboard.eventos_recientes) >= 1

    def test_obtener_dashboard_con_blog_stats(self, db):
        sitio = _crear_sitio_con_modulos(db)
        from app.packages.modulos.blog.models import Post, PostStatus
        from app.models.sitio import Sitio
        from app.models.modulo import Modulo
        site_id = sitio.id

        for i in range(3):
            db.add(Post(site_id=site_id, title=f"Post {i}", slug=f"post-{i}", status=PostStatus.PUBLISHED, content="x"))
        db.commit()

        dashboard = services.obtener_dashboard(db, site_id, dias=7)
        assert dashboard.blog is not None
        assert dashboard.blog.total_posts == 3
        assert dashboard.blog.publicados == 3

    def test_obtener_dashboard_con_tienda_stats(self, db):
        sitio = _crear_sitio_con_modulos(db)
        from app.packages.modulos.store.models import Producto, Pedido, PedidoEstado, ItemPedido
        site_id = sitio.id

        db.add(Producto(site_id=site_id, nombre="Prod A", slug="prod-a", precio=100, es_activo=True, descripcion="x"))
        db.add(Producto(site_id=site_id, nombre="Prod B", slug="prod-b", precio=200, es_activo=True, descripcion="x"))
        pedido = Pedido(
            site_id=site_id, numero_pedido="PED-001",
            subtotal=300, total=300, estado=PedidoEstado.ENTREGADO,
            nombre_cliente="Test", email_cliente="test@test.com",
        )
        db.add(pedido)
        db.flush()
        db.add(ItemPedido(pedido_id=pedido.id, nombre_producto="Prod A", cantidad=2, precio_unitario=100, total=200))
        db.add(ItemPedido(pedido_id=pedido.id, nombre_producto="Prod B", cantidad=1, precio_unitario=100, total=100))
        db.commit()

        dashboard = services.obtener_dashboard(db, site_id, dias=7)
        assert dashboard.tienda is not None
        assert dashboard.tienda.total_productos == 2
        assert dashboard.tienda.total_pedidos == 1
        assert dashboard.tienda.ingresos_totales == 300.0


class TestDetectores:
    @pytest.mark.parametrize("ua,esperado", [
        ("Mozilla/5.0 Chrome/120", "Chrome"),
        ("Mozilla/5.0 Edge/120", "Edge"),
        ("Mozilla/5.0 Firefox/120", "Firefox"),
        ("Mozilla/5.0 Safari/605", "Safari"),
        ("Opera/9.80", "Opera"),
        ("Mozilla/5.0 OPR/80", "Opera"),
        (None, None),
        ("Some Unknown Browser", "Otros"),
    ])
    def test_detectar_navegador(self, ua, esperado):
        assert services._detectar_navegador(ua) == esperado

    @pytest.mark.parametrize("ua,esperado", [
        ("Mozilla/5.0 Android", "Móvil"),
        ("Mozilla/5.0 iPhone", "Móvil"),
        ("Mozilla/5.0 Mobile", "Móvil"),
        ("Mozilla/5.0 iPad", "Tablet"),
        ("Mozilla/5.0 Tablet", "Tablet"),
        ("Mozilla/5.0 Windows", "Desktop"),
        (None, None),
    ])
    def test_detectar_dispositivo(self, ua, esperado):
        assert services._detectar_dispositivo(ua) == esperado
