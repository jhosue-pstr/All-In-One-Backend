import pytest


class TestRolesEndpoints:
    def test_mis_permisos(self, client):
        response = client.get("/api/roles/mis-permisos")
        assert response.status_code == 200
        data = response.json()
        assert "usuario_id" in data
        assert "correo" in data
        assert "role" in data
        assert "permisos" in data
        assert len(data["permisos"]) > 0

    def test_listar_permisos(self, client):
        response = client.get("/api/roles/permisos")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_listar_roles(self, client):
        response = client.get("/api/roles")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "codigo" in data[0]

    def test_crear_rol(self, client):
        response = client.post("/api/roles", json={
            "nombre": "Test Rol",
            "codigo": "test-rol",
            "descripcion": "Rol de prueba",
            "permisos": ["inicio.ver", "blog.ver"],
        })
        assert response.status_code == 201
        data = response.json()
        assert data["codigo"] == "test-rol"
        assert data["es_sistema"] is False
        assert "inicio.ver" in data["permisos"]
        assert "blog.ver" in data["permisos"]

    def test_crear_rol_duplicado(self, client):
        client.post("/api/roles", json={
            "nombre": "Dupe", "codigo": "rol-dupe", "permisos": [],
        })
        response = client.post("/api/roles", json={
            "nombre": "Dupe", "codigo": "rol-dupe", "permisos": [],
        })
        assert response.status_code == 400

    def test_crear_rol_codigo_reservado(self, client):
        response = client.post("/api/roles", json={
            "nombre": "Admin", "codigo": "admin", "permisos": [],
        })
        assert response.status_code == 400

    def test_actualizar_rol(self, client):
        create_resp = client.post("/api/roles", json={
            "nombre": "Original", "codigo": "actualizable", "permisos": ["inicio.ver"],
        })
        rol_id = create_resp.json()["id"]

        response = client.put(f"/api/roles/{rol_id}", json={
            "nombre": "Actualizado",
            "descripcion": "Nueva desc",
            "permisos": ["blog.ver"],
        })
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Actualizado"
        assert "blog.ver" in data["permisos"]
        assert "inicio.ver" not in data["permisos"]

    def test_actualizar_rol_sistema(self, client):
        roles = client.get("/api/roles").json()
        sa_rol = next(r for r in roles if r["codigo"] == "super_admin")
        response = client.put(f"/api/roles/{sa_rol['id']}", json={"nombre": "X"})
        assert response.status_code == 400

    def test_eliminar_rol(self, client):
        create_resp = client.post("/api/roles", json={
            "nombre": "Eliminable", "codigo": "eliminable", "permisos": [],
        })
        rol_id = create_resp.json()["id"]

        response = client.delete(f"/api/roles/{rol_id}")
        assert response.status_code == 200
        assert response.json()["mensaje"] == "Rol desactivado correctamente"

    def test_eliminar_rol_sistema(self, client):
        roles = client.get("/api/roles").json()
        sa_rol = next(r for r in roles if r["codigo"] == "user")
        response = client.delete(f"/api/roles/{sa_rol['id']}")
        assert response.status_code == 400

    def test_listar_usuarios(self, client):
        response = client.get("/api/roles/usuarios")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_crear_usuario_sistema(self, client):
        response = client.post("/api/roles/usuarios", json={
            "correo": "sistema@test.com",
            "contrasena": "123456",
            "nombre": "Sistema",
            "apellido": "User",
            "role": "admin",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["correo"] == "sistema@test.com"
        assert data["role"] == "admin"

    def test_cambiar_rol_usuario(self, client):
        user_resp = client.post("/api/roles/usuarios", json={
            "correo": "cambiar@test.com",
            "contrasena": "123456",
            "nombre": "Cambiar",
            "apellido": "User",
            "role": "user",
        })
        user_id = user_resp.json()["id"]

        response = client.put(f"/api/roles/usuarios/{user_id}/rol", json={"role": "admin"})
        assert response.status_code == 200
        assert response.json()["role"] == "admin"

    def test_desactivar_activar_usuario(self, client):
        user_resp = client.post("/api/roles/usuarios", json={
            "correo": "toggle@test.com",
            "contrasena": "123456",
            "nombre": "Toggle",
            "apellido": "User",
            "role": "user",
        })
        user_id = user_resp.json()["id"]

        delete_resp = client.delete(f"/api/roles/usuarios/{user_id}")
        assert delete_resp.status_code == 200

        activate_resp = client.put(f"/api/roles/usuarios/{user_id}/activar")
        assert activate_resp.status_code == 200
        assert activate_resp.json()["activo"] is True

    def test_403_sin_permiso(self, client):
        from app.models.usuario import User
        from app.db.database import SessionLocal
        from app.models.rol import Rol, RolPermiso

        db = SessionLocal()
        try:
            rol_sin_permisos = db.query(Rol).filter(Rol.codigo == "user").first()
            db.query(RolPermiso).filter(RolPermiso.rol_id == rol_sin_permisos.id).delete()
            db.commit()
        finally:
            db.close()

        client.post("/api/auth/registro", json={
            "correo": "no-perm@test.com", "contrasena": "123456",
            "nombre": "No", "apellido": "Perm",
        })
        login = client.post("/api/auth/inicio", data={
            "username": "no-perm@test.com", "password": "123456",
        })
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/roles/permisos", headers=headers)
        assert response.status_code == 403
