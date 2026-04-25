def test_create_modulo_duplicate_error(db):
    from app.service.modulo import create_modulo
    from app.schemas.modulo import ModuloCreate
    from sqlalchemy.exc import SQLAlchemyError
    
    data = ModuloCreate(nombre="Test", slug="dup-test", tipo="test")
    create_modulo(db, data)
    
    with pytest.raises(SQLAlchemyError):
        create_modulo(db, data)