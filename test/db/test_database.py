from app.db.database import get_db, Base, engine, SessionLocal


def test_database_base_exists():
    assert Base is not None


def test_database_sessionlocal_exists():
    assert SessionLocal is not None


def test_database_engine_exists():
    assert engine is not None


def test_get_db_is_generator(db):
    from app.db.database import get_db
    
    gen = get_db()
    assert hasattr(gen, '__next__')
    
    db_instance = next(gen)
    assert db_instance is not None
    
    try:
        next(gen)
    except StopIteration:
        pass