import runpy

from app.db.seed_sitios import seed_sitios, seed_blog_data
from app.models.sitio import Sitio
from app.packages.modulos.blog.models import Post, Category as BlogCategory
from app.packages.modulos.store.models import Producto, Categoria as TiendaCategoria


def test_seed_sitios_creates_sitios(db):
    seed_sitios(db)

    sitios = db.query(Sitio).all()
    assert len(sitios) == 3

    slugs = [s.slug for s in sitios]
    assert "abogado-demo" in slugs
    assert "blog-demo" in slugs
    assert "tienda-demo" in slugs


def test_seed_sitios_idempotent(db):
    seed_sitios(db)
    count_after_first = db.query(Sitio).count()

    seed_sitios(db)
    count_after_second = db.query(Sitio).count()

    assert count_after_first == count_after_second == 3


def test_seed_sitios_abogado_data(db):
    seed_sitios(db)

    sitio = db.query(Sitio).filter(Sitio.slug == "abogado-demo").first()
    assert sitio is not None
    assert sitio.nombre == "Estudio Jurídico Pérez & Asociados"
    assert sitio.activo is True
    assert sitio.switches == {}


def test_seed_sitios_blog_creates_categories_and_posts(db):
    seed_sitios(db)

    sitio = db.query(Sitio).filter(Sitio.slug == "blog-demo").first()
    assert sitio is not None

    categorias = db.query(BlogCategory).filter(BlogCategory.site_id == sitio.id).all()
    assert len(categorias) == 3

    posts = db.query(Post).filter(Post.site_id == sitio.id).all()
    assert len(posts) == 4


def test_seed_sitios_blog_idempotent_skips(db):
    seed_sitios(db)
    sitio = db.query(Sitio).filter(Sitio.slug == "blog-demo").first()

    posts_after_first = db.query(Post).filter(Post.site_id == sitio.id).count()

    seed_sitios(db)
    posts_after_second = db.query(Post).filter(Post.site_id == sitio.id).count()

    assert posts_after_first == posts_after_second == 4


def test_seed_sitios_tienda_creates_categories_and_products(db):
    seed_sitios(db)

    sitio = db.query(Sitio).filter(Sitio.slug == "tienda-demo").first()
    assert sitio is not None

    categorias = db.query(TiendaCategoria).filter(TiendaCategoria.site_id == sitio.id).all()
    assert len(categorias) == 3

    productos = db.query(Producto).filter(Producto.site_id == sitio.id).all()
    assert len(productos) == 6


def test_seed_sitios_tienda_idempotent_skips(db):
    seed_sitios(db)
    sitio = db.query(Sitio).filter(Sitio.slug == "tienda-demo").first()

    productos_after_first = db.query(Producto).filter(Producto.site_id == sitio.id).count()

    seed_sitios(db)
    productos_after_second = db.query(Producto).filter(Producto.site_id == sitio.id).count()

    assert productos_after_first == productos_after_second == 6


def test_seed_sitios_cubre_sitio_existente(db):
    sitio = Sitio(
        slug="abogado-demo",
        nombre="Abogado Existente",
        activo=True,
        configuracion={},
        switches={}
    )
    db.add(sitio)
    db.commit()

    seed_sitios(db)

    assert db.query(Sitio).filter(Sitio.slug == "abogado-demo").count() == 1


def test_seed_blog_data_existente_return(db):
    sitio = Sitio(
        slug="blog-existente-return",
        nombre="Blog Existente Return",
        activo=True,
        configuracion={},
        switches={}
    )
    db.add(sitio)
    db.commit()
    db.refresh(sitio)

    categoria = BlogCategory(
        site_id=sitio.id,
        name="General",
        slug="general",
        description="Ya existe"
    )
    db.add(categoria)
    db.commit()

    seed_blog_data(db, sitio.id)

    assert db.query(BlogCategory).filter(BlogCategory.site_id == sitio.id).count() == 1


def test_seed_sitios_main():
    runpy.run_module(
        "app.db.seed_sitios",
        run_name="__main__"
    )