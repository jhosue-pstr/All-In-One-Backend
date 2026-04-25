from app.db.seed_modulos import seed_modulos
from app.models.modulo import Modulo


def test_seed_modulos_creates_site_auth(db, monkeypatch):
    from app.db import seed_modulos as sm
    
    def mock_session(engine):
        return db
    
    monkeypatch.setattr(sm, "Session", mock_session)
    seed_modulos()
    
    modulo = db.query(Modulo).filter(Modulo.slug == "site-auth").first()
    
    assert modulo is not None
    assert modulo.nombre == "SiteAuth"
    assert modulo.tipo == "auth"
    assert modulo.activo is True


def test_seed_modulos_does_not_duplicate(db, monkeypatch):
    from app.db import seed_modulos as sm
    
    def mock_session(engine):
        return db
    
    monkeypatch.setattr(sm, "Session", mock_session)
    seed_modulos()
    seed_modulos()
    
    count = db.query(Modulo).filter(Modulo.slug == "site-auth").count()
    
    assert count == 1


def test_seed_modulos_configuracion_base(db, monkeypatch):
    from app.db import seed_modulos as sm
    
    def mock_session(engine):
        return db
    
    monkeypatch.setattr(sm, "Session", mock_session)
    seed_modulos()
    
    modulo = db.query(Modulo).filter(Modulo.slug == "site-auth").first()
    
    assert modulo.configuracion_base is not None
    assert modulo.configuracion_base["enabled"] is True
    assert modulo.configuracion_base["allow_registration"] is True