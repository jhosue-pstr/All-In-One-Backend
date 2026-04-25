def test_seed_modulos_main_block():
    import app.db.seed_modulos as seed_modulos
    import inspect
    
    source = inspect.getsource(seed_modulos)
    assert 'if __name__ == "__main__"' in source


def test_seed_modulos_creates_site_auth(db, monkeypatch):
    from app.db import seed_modulos as sm
    
    def mock_session(engine):
        return db
    
    monkeypatch.setattr(sm, "Session", mock_session)
    sm.seed_modulos()
    
    from app.models.modulo import Modulo
    modulo = db.query(Modulo).filter(Modulo.slug == "site-auth").first()
    
    assert modulo is not None