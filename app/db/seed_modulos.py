from sqlalchemy.orm import Session
from app.db.database import engine
from app.models.modulo import Modulo


def seed_modulos():
    """Agrega módulos base a la DB si no existen"""
    
    modulos_base = [
        {
            "nombre": "SiteAuth",
            "slug": "site-auth",
            "descripcion": "Módulo de autenticación (login, registro, perfil)",
            "tipo": "auth",
            "configuracion_base": {
                "enabled": True,
                "allow_registration": True
            },
            "activo": True
        },
    ]
    
    with Session(engine) as db:
        for mod_data in modulos_base:
            existente = db.query(Modulo).filter(Modulo.slug == mod_data["slug"]).first()
            if not existente:
                modulo = Modulo(**mod_data)
                db.add(modulo)
                print(f"✓ Módulo '{mod_data['nombre']}' creado")
        
        db.commit()
    print("✓ Seed de módulos completado")


if __name__ == "__main__":
    seed_modulos()
