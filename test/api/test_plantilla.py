from app.schemas.plantilla import PlantillaCreate, PlantillaUpdate
from app.service.plantilla import (
    create_plantilla,
    
    get_plantilla,
    get_plantillas_publicas,
    get_plantillas_del_usuario,
    update_plantilla,
    delete_plantilla,
    es_propietario,
)
from app.models.plantilla import Plantilla, Visibilidad


def test_crear_plantilla_asigna_usuario(db, user):
    data = PlantillaCreate(nombre="Plantilla 1", slug="plantilla-1")

    plantilla = create_plantilla(db, data, user.id)

    assert plantilla.id is not None
    assert plantilla.nombre == "Plantilla 1"
    assert plantilla.slug == "plantilla-1"
    assert plantilla.id_usuario == user.id
    assert plantilla.visibilidad == Visibilidad.PRIVADA


def test_crear_plantilla_publica(db, user):
    data = PlantillaCreate(nombre="Publica", slug="publica", visibilidad=Visibilidad.PUBLICA)

    plantilla = create_plantilla(db, data, user.id)

    assert plantilla.visibilidad == Visibilidad.PUBLICA


def test_obtener_plantilla(db):
    from app.models.plantilla import Plantilla

    obj = Plantilla(nombre="Test", slug="test", visibilidad=Visibilidad.PUBLICA)
    db.add(obj)
    db.commit()
    db.refresh(obj)

    result = get_plantilla(db, obj.id)

    assert result is not None
    assert result.id == obj.id


def test_obtener_plantillas_publicas(db, user):
    db.add_all([
        Plantilla(nombre="Publica", slug="publica-a", visibilidad=Visibilidad.PUBLICA),
        Plantilla(nombre="Privada", slug="privada-a", visibilidad=Visibilidad.PRIVADA, id_usuario=user.id),
    ])
    db.commit()

    result = get_plantillas_publicas(db)

    assert all(p.visibilidad == Visibilidad.PUBLICA for p in result)


def test_obtener_plantillas_del_usuario(db, user):
    db.add_all([
        Plantilla(nombre="Mi Plantilla", slug="mi-plantilla-a", id_usuario=user.id),
        Plantilla(nombre="Otra", slug="otra-a", visibilidad=Visibilidad.PUBLICA),
    ])
    db.commit()

    result = get_plantillas_del_usuario(db, user.id)

    assert len(result) >= 1


def test_actualizar_plantilla(db):
    from app.models.plantilla import Plantilla

    obj = Plantilla(nombre="Old", slug="old")
    db.add(obj)
    db.commit()
    db.refresh(obj)

    update_data = PlantillaUpdate(nombre="New")

    updated = update_plantilla(db, obj.id, update_data)

    assert updated.nombre == "New"


def test_eliminar_plantilla(db):
    from app.models.plantilla import Plantilla

    obj = Plantilla(nombre="Delete", slug="delete")
    db.add(obj)
    db.commit()
    db.refresh(obj)

    delete_plantilla(db, obj.id)

    # El test ahora busca el objeto físico en la BD
    result = db.query(Plantilla).filter(Plantilla.id == obj.id).first()

    # Comprobamos el Soft Delete
    assert result is not None, "El registro físico no debería borrarse"
    assert result.activo is False, "El estado debió cambiar a False"

def test_upload_miniatura_exitoso_final(client):
    """Cubre el return final de upload_miniatura al 100% con un caso de éxito real"""
    client.post("/api/auth/registro", json={"correo": "foto_final@test.com", "contrasena": "123", "nombre": "A", "apellido": "B"})
    login = client.post("/api/auth/inicio", data={"username": "foto_final@test.com", "password": "123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    create_resp = client.post("/api/plantillas", json={"nombre": "Foto", "slug": "foto-final"}, headers=headers)
    pid = create_resp.json()["id"]
    
    files = {"file": ("foto.png", b"data de prueba", "image/png")}
    response = client.post(f"/api/plantillas/{pid}/miniatura", files=files, headers=headers)
    
    assert response.status_code == 200
    assert "url" in response.json()

def test_get_publicas_directo(client):
    """Cubre la línea 36 (Ruta /publicas) directamente en este archivo"""
    response = client.get("/api/plantillas/publicas")
    assert response.status_code == 200

def test_get_mis_plantillas_directo(client):
    """Cubre la línea 44 (Ruta /mis-plantillas) directamente en este archivo"""
    client.post("/api/auth/registro", json={"correo": "mis_plan_dir@test.com", "contrasena": "123", "nombre": "A", "apellido": "B"})
    login = client.post("/api/auth/inicio", data={"username": "mis_plan_dir@test.com", "password": "123"})
    token = login.json()["access_token"]
    
    response = client.get("/api/plantillas/mis-plantillas", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_fuerza_bruta_miniatura_return(db, user):
    """Cubre la línea 136 inyectando el request directamente al router"""
    from app.api.plantilla import upload_miniatura
    from app.models.plantilla import Plantilla
    from fastapi import Request
    from starlette.datastructures import Headers
    from io import BytesIO
    
    class FakeUploadFile:
        filename = "test.png"
        file = BytesIO(b"fake")
        
    request = Request({
        "type": "http",
        "headers": Headers({"host": "testserver"}).raw,
        "scheme": "http",
        "server": ("testserver", 80),
        "path": "/",
        "query_string": b"",
    })
    
    p = Plantilla(nombre="FB-Return", slug="fb-ret", id_usuario=user.id)
    db.add(p)
    db.commit()
    db.refresh(p)
    
    result = upload_miniatura(plantilla_id=p.id, request=request, current_user=user, db=db, file=FakeUploadFile())
    assert result is not None