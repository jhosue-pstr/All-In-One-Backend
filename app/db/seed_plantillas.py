"""Seed de plantillas demo basadas en los sitios demo"""

from sqlalchemy.orm import Session
from app.db.database import engine
from app.models.plantilla import Plantilla, Visibilidad
from app.db.seed_sitios import ABOGADO_HTML, BLOG_HTML, TIENDA_HTML


def seed_plantillas():
    plantillas_data = [
        {
            "slug": "plantilla-abogado",
            "nombre": "Landing Page - Abogado",
            "descripcion": "Plantilla profesional para estudios jurídicos con hero, servicios, nosotros, features, testimonios, FAQ, contacto y footer.",
            "visibilidad": Visibilidad.PUBLICA,
            "activo": True,
            "id_usuario": None,
            "configuracion": {
                "html": ABOGADO_HTML,
                "css": "",
                "js": "",
            },
        },
        {
            "slug": "plantilla-blog",
            "nombre": "Blog de Noticias",
            "descripcion": "Plantilla de blog con bloque destacado, grilla de posts, buscador y categorías. Incluye datos demo de posts y categorías.",
            "visibilidad": Visibilidad.PUBLICA,
            "activo": True,
            "id_usuario": None,
            "configuracion": {
                "html": BLOG_HTML,
                "css": "",
                "js": "",
            },
        },
        {
            "slug": "plantilla-tienda",
            "nombre": "Tienda Online",
            "descripcion": "Plantilla de e-commerce con categorías, producto destacado, grilla de productos, carrito de compras y checkout. Incluye datos demo de productos y categorías.",
            "visibilidad": Visibilidad.PUBLICA,
            "activo": True,
            "id_usuario": None,
            "configuracion": {
                "html": TIENDA_HTML,
                "css": "",
                "js": "",
            },
        },
    ]

    with Session(engine) as db:
        for data in plantillas_data:
            slug = data["slug"]
            existente = db.query(Plantilla).filter(Plantilla.slug == slug).first()
            if existente:
                print(f"  Plantilla '{slug}' ya existe (id={existente.id})")
            else:
                plantilla = Plantilla(**data)
                db.add(plantilla)
                db.flush()
                print(f"  Plantilla '{slug}' creada (id={plantilla.id})")

        db.commit()
    print(" Seed de plantillas completado")


if __name__ == "__main__":
    seed_plantillas()
