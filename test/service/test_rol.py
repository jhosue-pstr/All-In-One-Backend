import pytest
from fastapi import HTTPException

from app.service.rol import RolService, get_password_hash
from app.models.usuario import User
from app.models.rol import Rol, Permiso, RolPermiso
from app.models.auditoria import Auditoria
from app.schemas.rol import RolCreate, RolUpdate, UsuarioSistemaCreate


@pytest.fixture
def super_admin(db):
    user = User(
        correo="super@test.com", contrasena="hash",
        nombre="Super", apellido="Admin",
        role="super_admin", activo=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def usuario_normal(db):
    user = User(
        correo="normal@test.com", contrasena="hash",
        nombre="Normal", apellido="User",
        role="user", activo=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _crear_rol_custom(db, codigo="custom_role", permisos=None):
    rol = Rol(nombre="Custom", codigo=codigo, descripcion="Test", activo=True, es_sistema=False)
    db.add(rol)
    db.flush()
    if permisos:
        for p_codigo in permisos:
            permiso = db.query(Permiso).filter(Permiso.codigo == p_codigo).first()
            if permiso:
                db.add(RolPermiso(rol_id=rol.id, permiso_id=permiso.id))
    db.commit()
    db.refresh(rol)
    return rol


class TestRolService:
    def test_get_password_hash(self):
        h = get_password_hash("test123")
        assert isinstance(h, str)
        assert len(h) > 20
        assert h != "test123"

    def test_listar_permisos(self, db):
        svc = RolService(db)
        permisos = svc.listar_permisos()
        assert len(permisos) > 0
        assert all(p.activo for p in permisos)

    def test_listar_roles(self, db):
        svc = RolService(db)
        roles = svc.listar_roles()
        assert len(roles) > 0
        assert all(r.activo for r in roles)

    def test_obtener_rol_por_codigo_found(self, db):
        svc = RolService(db)
        rol = svc.obtener_rol_por_codigo("super_admin")
        assert rol is not None
        assert rol.codigo == "super_admin"

    def test_obtener_rol_por_codigo_not_found(self, db):
        svc = RolService(db)
        assert svc.obtener_rol_por_codigo("no_existe") is None

    def test_obtener_rol_found(self, db):
        svc = RolService(db)
        rol = db.query(Rol).filter(Rol.codigo == "super_admin").first()
        result = svc.obtener_rol(rol.id)
        assert result.id == rol.id

    def test_obtener_rol_not_found(self, db):
        svc = RolService(db)
        with pytest.raises(HTTPException) as exc:
            svc.obtener_rol(99999)
        assert exc.value.status_code == 404

    def test_crear_rol_success(self, db, super_admin):
        svc = RolService(db)
        data = RolCreate(
            nombre="Mi Rol",
            codigo="mi-rol",
            descripcion="Un rol de prueba",
            permisos=["inicio.ver", "blog.ver"],
        )
        rol = svc.crear_rol(data, super_admin.id)
        assert rol.id is not None
        assert rol.codigo == "mi-rol"
        assert rol.es_sistema is False

        perms = {rp.permiso.codigo for rp in rol.permisos if rp.permiso}
        assert "inicio.ver" in perms
        assert "blog.ver" in perms

        audit = db.query(Auditoria).filter(
            Auditoria.entidad == "roles",
            Auditoria.entidad_id == rol.id,
            Auditoria.accion == "INSERT",
        ).first()
        assert audit is not None

    def test_crear_rol_codigo_reservado(self, db, super_admin):
        svc = RolService(db)
        for codigo in ["super_admin", "admin", "editor_sitios", "gestor_contenido", "gestor_tienda", "auditor", "user"]:
            data = RolCreate(nombre="X", codigo=codigo, permisos=[])
            with pytest.raises(HTTPException) as exc:
                svc.crear_rol(data, super_admin.id)
            assert exc.value.status_code == 400

    def test_crear_rol_codigo_duplicado(self, db, super_admin):
        svc = RolService(db)
        data = RolCreate(nombre="X", codigo="mi-rol-dupe", permisos=[])
        svc.crear_rol(data, super_admin.id)
        with pytest.raises(HTTPException) as exc:
            svc.crear_rol(data, super_admin.id)
        assert exc.value.status_code == 400

    def test_crear_rol_not_super_admin(self, db, usuario_normal):
        svc = RolService(db)
        data = RolCreate(nombre="X", codigo="x", permisos=[])
        with pytest.raises(HTTPException) as exc:
            svc.crear_rol(data, usuario_normal.id)
        assert exc.value.status_code == 403

    def test_actualizar_rol_success(self, db, super_admin):
        svc = RolService(db)
        rol = _crear_rol_custom(db, "updatable", ["inicio.ver"])

        data = RolUpdate(nombre="NuevoNombre", descripcion="Nueva desc", activo=True, permisos=["blog.ver"])
        updated = svc.actualizar_rol(rol.id, data, super_admin.id)
        assert updated.nombre == "NuevoNombre"
        assert updated.descripcion == "Nueva desc"

        perms = {rp.permiso.codigo for rp in updated.permisos if rp.permiso}
        assert "blog.ver" in perms
        assert "inicio.ver" not in perms

        audit = db.query(Auditoria).filter(
            Auditoria.entidad == "roles",
            Auditoria.entidad_id == rol.id,
            Auditoria.accion == "UPDATE",
        ).first()
        assert audit is not None

    def test_actualizar_rol_sistema(self, db, super_admin):
        svc = RolService(db)
        rol = db.query(Rol).filter(Rol.codigo == "user").first()
        data = RolUpdate(nombre="X")
        with pytest.raises(HTTPException) as exc:
            svc.actualizar_rol(rol.id, data, super_admin.id)
        assert exc.value.status_code == 400

    def test_actualizar_rol_not_found(self, db, super_admin):
        svc = RolService(db)
        data = RolUpdate(nombre="X")
        with pytest.raises(HTTPException) as exc:
            svc.actualizar_rol(99999, data, super_admin.id)
        assert exc.value.status_code == 404

    def test_actualizar_rol_not_super_admin(self, db, usuario_normal):
        svc = RolService(db)
        rol = _crear_rol_custom(db, "no-perm")
        data = RolUpdate(nombre="X")
        with pytest.raises(HTTPException) as exc:
            svc.actualizar_rol(rol.id, data, usuario_normal.id)
        assert exc.value.status_code == 403

    def test_eliminar_rol_success(self, db, super_admin):
        svc = RolService(db)
        rol = _crear_rol_custom(db, "deletable", ["inicio.ver"])
        result = svc.eliminar_rol(rol.id, super_admin.id)
        assert "mensaje" in result
        db.refresh(rol)
        assert rol.activo is False

        audit = db.query(Auditoria).filter(
            Auditoria.entidad == "roles",
            Auditoria.entidad_id == rol.id,
            Auditoria.accion == "DELETE",
        ).first()
        assert audit is not None

    def test_eliminar_rol_sistema(self, db, super_admin):
        svc = RolService(db)
        rol = db.query(Rol).filter(Rol.codigo == "user").first()
        with pytest.raises(HTTPException) as exc:
            svc.eliminar_rol(rol.id, super_admin.id)
        assert exc.value.status_code == 400

    def test_eliminar_rol_con_usuarios(self, db, super_admin):
        svc = RolService(db)
        rol = _crear_rol_custom(db, "has-users")
        db.add(User(correo="asignado@test.com", contrasena="hash", nombre="A", apellido="B", role="has-users", activo=True))
        db.commit()
        with pytest.raises(HTTPException) as exc:
            svc.eliminar_rol(rol.id, super_admin.id)
        assert exc.value.status_code == 400

    def test_eliminar_rol_not_super_admin(self, db, usuario_normal):
        svc = RolService(db)
        rol = _crear_rol_custom(db, "no-super")
        with pytest.raises(HTTPException) as exc:
            svc.eliminar_rol(rol.id, usuario_normal.id)
        assert exc.value.status_code == 403

    def test_listar_usuarios(self, db, super_admin):
        svc = RolService(db)
        usuarios = svc.listar_usuarios()
        assert len(usuarios) >= 1

    def test_crear_usuario_sistema_success(self, db, super_admin):
        svc = RolService(db)
        data = UsuarioSistemaCreate(
            correo="nuevo@test.com",
            contrasena="123456",
            nombre="Nuevo",
            apellido="User",
            role="admin",
        )
        user = svc.crear_usuario_sistema(data, super_admin.id)
        assert user.id is not None
        assert user.correo == "nuevo@test.com"
        assert user.role == "admin"

        audit = db.query(Auditoria).filter(
            Auditoria.entidad == "users",
            Auditoria.entidad_id == user.id,
            Auditoria.accion == "INSERT",
        ).first()
        assert audit is not None

    def test_crear_usuario_sistema_email_duplicado(self, db, super_admin):
        svc = RolService(db)
        data = UsuarioSistemaCreate(
            correo="dup@test.com", contrasena="123",
            nombre="D", apellido="UP", role="admin",
        )
        svc.crear_usuario_sistema(data, super_admin.id)
        with pytest.raises(HTTPException) as exc:
            svc.crear_usuario_sistema(data, super_admin.id)
        assert exc.value.status_code == 400

    def test_crear_usuario_sistema_rol_invalido(self, db, super_admin):
        svc = RolService(db)
        data = UsuarioSistemaCreate(
            correo="bad@test.com", contrasena="123",
            nombre="B", apellido="AD", role="no_existe",
        )
        with pytest.raises(HTTPException) as exc:
            svc.crear_usuario_sistema(data, super_admin.id)
        assert exc.value.status_code == 400

    def test_cambiar_rol_usuario_success(self, db, super_admin, usuario_normal):
        svc = RolService(db)
        result = svc.cambiar_rol_usuario(usuario_normal.id, "admin", super_admin.id)
        assert result.role == "admin"

        audit = db.query(Auditoria).filter(
            Auditoria.entidad == "users",
            Auditoria.entidad_id == usuario_normal.id,
            Auditoria.accion == "UPDATE",
        ).first()
        assert audit is not None

    def test_cambiar_rol_usuario_not_found(self, db, super_admin):
        svc = RolService(db)
        with pytest.raises(HTTPException) as exc:
            svc.cambiar_rol_usuario(99999, "admin", super_admin.id)
        assert exc.value.status_code == 404

    def test_cambiar_rol_usuario_auto_demotion(self, db, super_admin):
        svc = RolService(db)
        with pytest.raises(HTTPException) as exc:
            svc.cambiar_rol_usuario(super_admin.id, "user", super_admin.id)
        assert exc.value.status_code == 400

    def test_validar_super_admin_activo_minimo_raise(self, db):
        svc = RolService(db)
        sa = User(correo="sa@test.com", contrasena="hash", nombre="SA", apellido="X", role="super_admin", activo=True)
        db.add(sa)
        db.commit()
        db.refresh(sa)
        with pytest.raises(HTTPException) as exc:
            svc._validar_super_admin_activo_minimo(sa)
        assert exc.value.status_code == 400

    def test_validar_super_admin_activo_minimo_pass(self, db, super_admin):
        svc = RolService(db)
        otro_sa = User(correo="sa2@test.com", contrasena="hash", nombre="SA2", apellido="X", role="super_admin", activo=True)
        db.add(otro_sa)
        db.commit()
        svc._validar_super_admin_activo_minimo(otro_sa)

    def test_validar_accion_sobre_super_admin_raise(self, db):
        svc = RolService(db)
        normal = User(correo="n@test.com", contrasena="hash", nombre="N", apellido="X", role="user", activo=True)
        sa = User(correo="sa3@test.com", contrasena="hash", nombre="SA3", apellido="X", role="super_admin", activo=True)
        db.add_all([normal, sa])
        db.commit()
        with pytest.raises(HTTPException) as exc:
            svc._validar_accion_sobre_super_admin(sa, normal)
        assert exc.value.status_code == 403

    def test_validar_accion_sobre_super_admin_pass_sa_acting(self, db, super_admin):
        svc = RolService(db)
        svc._validar_accion_sobre_super_admin(super_admin, super_admin)

    def test_validar_accion_sobre_super_admin_pass_normal_target(self, db, super_admin):
        svc = RolService(db)
        normal = User(correo="n2@test.com", contrasena="hash", nombre="N2", apellido="X", role="user", activo=True)
        svc._validar_accion_sobre_super_admin(normal, super_admin)

    def test_cambiar_rol_usuario_asignar_super_admin_sin_serlo(self, db, usuario_normal):
        svc = RolService(db)
        otro = User(
            correo="otro@test.com", contrasena="hash",
            nombre="Otro", apellido="Test",
            role="user", activo=True,
        )
        db.add(otro)
        db.commit()
        with pytest.raises(HTTPException) as exc:
            svc.cambiar_rol_usuario(otro.id, "super_admin", usuario_normal.id)
        assert exc.value.status_code == 403

    def test_desactivar_usuario_success(self, db, super_admin, usuario_normal):
        svc = RolService(db)
        result = svc.desactivar_usuario(usuario_normal.id, super_admin.id)
        assert "mensaje" in result
        db.refresh(usuario_normal)
        assert usuario_normal.activo is False

        audit = db.query(Auditoria).filter(
            Auditoria.entidad == "users",
            Auditoria.entidad_id == usuario_normal.id,
            Auditoria.accion == "DELETE",
        ).first()
        assert audit is not None

    def test_desactivar_usuario_not_found(self, db, super_admin):
        svc = RolService(db)
        with pytest.raises(HTTPException) as exc:
            svc.desactivar_usuario(99999, super_admin.id)
        assert exc.value.status_code == 404

    def test_desactivar_usuario_self(self, db, super_admin):
        svc = RolService(db)
        with pytest.raises(HTTPException) as exc:
            svc.desactivar_usuario(super_admin.id, super_admin.id)
        assert exc.value.status_code == 400

    def test_desactivar_ultimo_super_admin(self, db, super_admin):
        svc = RolService(db)
        with pytest.raises(HTTPException) as exc:
            svc.desactivar_usuario(super_admin.id, super_admin.id)
        assert exc.value.status_code == 400

    def test_activar_usuario_success(self, db, super_admin, usuario_normal):
        usuario_normal.activo = False
        db.commit()
        svc = RolService(db)
        result = svc.activar_usuario(usuario_normal.id, super_admin.id)
        assert result.activo is True

        audit = db.query(Auditoria).filter(
            Auditoria.entidad == "users",
            Auditoria.entidad_id == usuario_normal.id,
            Auditoria.accion == "UPDATE",
        ).first()
        assert audit is not None

    def test_activar_usuario_not_found(self, db, super_admin):
        svc = RolService(db)
        with pytest.raises(HTTPException) as exc:
            svc.activar_usuario(99999, super_admin.id)
        assert exc.value.status_code == 404

    def test_obtener_permisos_usuario_super_admin(self, db):
        svc = RolService(db)
        from app.models.usuario import User
        sa = User(correo="sa@test.com", contrasena="hash", nombre="SA", apellido="X", role="super_admin", activo=True)
        permisos = svc.obtener_permisos_usuario(sa)
        assert len(permisos) > 0
        assert "inicio.ver" in permisos
        assert "blog.ver" in permisos

    def test_obtener_permisos_usuario_normal(self, db):
        svc = RolService(db)
        from app.models.usuario import User
        normal = User(correo="n@test.com", contrasena="hash", nombre="N", apellido="X", role="user", activo=True)
        permisos = svc.obtener_permisos_usuario(normal)
        assert len(permisos) > 0

    def test_obtener_permisos_usuario_rol_inactivo(self, db):
        svc = RolService(db)
        rol = db.query(Rol).filter(Rol.codigo == "user").first()
        rol.activo = False
        db.commit()
        from app.models.usuario import User
        normal = User(correo="n2@test.com", contrasena="hash", nombre="N", apellido="X", role="user", activo=True)
        permisos = svc.obtener_permisos_usuario(normal)
        assert permisos == []

    def test_obtener_usuario_actual_no_encontrado(self, db):
        svc = RolService(db)
        with pytest.raises(HTTPException) as exc:
            svc._obtener_usuario_actual(99999)
        assert exc.value.status_code == 401

    def test_usuario_actual_no_existe_no_raise_en_metodos_que_no_llaman_validacion(self, db):
        svc = RolService(db)
        assert len(svc.listar_permisos()) > 0
