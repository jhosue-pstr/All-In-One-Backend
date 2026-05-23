from fastapi.testclient import TestClient


def test_render_sitio_no_existe(client: TestClient):
    response = client.get("/no-existe-12345")
    assert response.status_code == 404
    assert "no encontrado" in response.text.lower()


def test_render_sitio_existente(client: TestClient, db):
    from app.models.sitio import Sitio

    sitio = Sitio(
        nombre="Sitio Prueba",
        slug="sitio-prueba",
        activo=True,
        configuracion={"html": "<html><body><h1>Hola Mundo</h1></body></html>"}
    )
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    response = client.get("/sitio-prueba")

    assert response.status_code == 200
    assert "Hola Mundo" in response.text


def test_render_sitio_con_css(client: TestClient, db):
    from app.models.sitio import Sitio

    sitio = Sitio(
        nombre="Sitio CSS",
        slug="sitio-css",
        activo=True,
        configuracion={
            "html": "<html><head></head><body><h1>Titulo</h1></body></html>",
            "css": "h1 { color: red; }"
        }
    )
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    response = client.get("/sitio-css")

    assert response.status_code == 200
    assert "<style>h1 { color: red; }</style>" in response.text


def test_render_sitio_con_js(client: TestClient, db):
    from app.models.sitio import Sitio

    sitio = Sitio(
        nombre="Sitio JS",
        slug="sitio-js",
        activo=True,
        configuracion={
            "html": "<html><body><h1>Titulo</h1></body></html>",
            "js": "console.log('hola');"
        }
    )
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    response = client.get("/sitio-js")

    assert response.status_code == 200
    assert "<script>console.log('hola');</script>" in response.text


def test_render_sitio_inactivo(client: TestClient, db):
    from app.models.sitio import Sitio

    sitio = Sitio(
        nombre="Sitio Inactivo",
        slug="sitio-inactivo",
        activo=False
    )
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    response = client.get("/sitio-inactivo")

    # Ahora esperamos un 404 porque el servicio filtra los inactivos
    assert response.status_code == 404
    assert "no encontrado" in response.text.lower()


def test_render_sitio_vacio(client: TestClient, db):
    from app.models.sitio import Sitio

    sitio = Sitio(nombre="Sitio Vacio", slug="sitio-vacio", activo=True)
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    response = client.get("/sitio-vacio")

    assert response.status_code == 200
    assert "construcción" in response.text.lower()

def test_render_sitio_sin_html(client, db):
    """Cubre la línea de inyección de recursos cuando NO hay HTML configurado"""
    from app.models.sitio import Sitio

    sitio = Sitio(
        nombre="Sitio Vacio Absoluto",
        slug="sitio-vacio-absoluto",
        activo=True,
        configuracion=None
    )
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    response = client.get("/sitio-vacio-absoluto")

    assert response.status_code == 200
    assert "construcción" in response.text.lower()

def test_render_sitio_inyector_recursos_alternativo(client, db):
    """Cubre las ramas 'else' del inyector de recursos (cuando no hay </head> o </body>)"""
    from app.models.sitio import Sitio

    sitio = Sitio(
        nombre="Sitio Roto",
        slug="sitio-roto",
        activo=True,
        configuracion={
            "html": "<div>Hola</div>", # Sin head ni body
            "css": "div {color: red;}",
            "js": "alert('hola');"
        }
    )
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    response = client.get("/sitio-roto")

    assert response.status_code == 200
    assert "<style>" in response.text
    assert "<script>" in response.text

def test_check_system(client: TestClient):
    response = client.get("/check-system")

    assert response.status_code == 200
    assert response.json() == {
        "blog": "ok",
        "tienda": "ok"
    }