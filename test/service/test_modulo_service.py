import pytest
from app.service.modulo import create_modulo
from app.schemas.modulo import ModuloCreate
from sqlalchemy.exc import IntegrityError


def test_create_modulo_duplicate_error(db):
    from app.models.modulo import Modulo

    db.add(Modulo(nombre="Test", slug="dup-test-svc", tipo="x"))
    db.commit()

    with pytest.raises(IntegrityError):
        create_modulo(db, ModuloCreate(nombre="Test2", slug="dup-test-svc", tipo="x"))