def test_sitio_modulo_table_in_metadata(db):
    from app.db.database import Base
    
    assert "sitio_modulos" in Base.metadata.tables


def test_sitio_modulo_table_structure(db):
    from app.db.database import Base
    
    table = Base.metadata.tables.get("sitio_modulos")
    assert table is not None
    
    columns = [c.name for c in table.columns]
    assert "sitio_id" in columns
    assert "modulo_id" in columns


def test_sitio_modulo_primary_keys(db):
    from app.db.database import Base
    
    table = Base.metadata.tables.get("sitio_modulos")
    pk_columns = [c.name for c in table.primary_key.columns]
    
    assert "sitio_id" in pk_columns
    assert "modulo_id" in pk_columns