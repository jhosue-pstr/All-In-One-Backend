from app.schemas.sitio_modulo import SitioModuloCreate, SitioModuloResponse


def test_sitio_modulo_create_schema():
    data = SitioModuloCreate(sitio_id=1, modulo_id=2)
    
    assert data.sitio_id == 1
    assert data.modulo_id == 2


def test_sitio_modulo_response_schema():
    data = SitioModuloResponse(sitio_id=1, modulo_id=2)
    
    assert data.sitio_id == 1
    assert data.modulo_id == 2


def test_sitio_modulo_response_to_dict():
    data = SitioModuloResponse(sitio_id=1, modulo_id=2)
    
    assert data.model_dump() == {"sitio_id": 1, "modulo_id": 2}