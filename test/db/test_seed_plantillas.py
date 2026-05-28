from app.db.database import Base
from app.db.seed_plantillas import seed_plantillas
from app.models.plantilla import Plantilla


def test_seed_plantillas_creates_plantillas(db):
    seed_plantillas()

    plantillas = db.query(Plantilla).all()
    assert len(plantillas) == 3

    slugs = [p.slug for p in plantillas]
    assert "plantilla-abogado" in slugs
    assert "plantilla-blog" in slugs
    assert "plantilla-tienda" in slugs


def test_seed_plantillas_idempotent(db):
    seed_plantillas()
    count_after_first = db.query(Plantilla).count()

    seed_plantillas()
    count_after_second = db.query(Plantilla).count()

    assert count_after_first == count_after_second == 3


def test_seed_plantillas_plantilla_abogado_data(db):
    seed_plantillas()

    abogado = db.query(Plantilla).filter(Plantilla.slug == "plantilla-abogado").first()
    assert abogado is not None
    assert abogado.nombre == "Landing Page - Abogado"
    assert abogado.activo is True
    assert "html" in abogado.configuracion
    assert "css" in abogado.configuracion
    assert "js" in abogado.configuracion


def test_seed_plantillas_plantilla_blog_data(db):
    seed_plantillas()

    blog = db.query(Plantilla).filter(Plantilla.slug == "plantilla-blog").first()
    assert blog is not None
    assert blog.nombre == "Blog de Noticias"
    assert blog.activo is True


def test_seed_plantillas_plantilla_tienda_data(db):
    seed_plantillas()

    tienda = db.query(Plantilla).filter(Plantilla.slug == "plantilla-tienda").first()
    assert tienda is not None
    assert tienda.nombre == "Tienda Online"
    assert tienda.activo is True
