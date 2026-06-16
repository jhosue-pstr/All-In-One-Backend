from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import bcrypt

from app.models.rol import Rol, Permiso, RolPermiso
from app.models.usuario import User
from app.models.auditoria import Auditoria
from app.schemas.rol import RolCreate, RolUpdate, UsuarioSistemaCreate

USUARIO_NO_ENCONTRADO = "Usuario no encontrado"
def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


class RolService:
    def __init__(self, db: Session):
        self.db = db

    def _auditar(
        self,
        entidad: str,
        entidad_id: int,
        accion: str,
        usuario_id: int | None,
        anteriores=None,
        nuevos=None,
    ):
        auditoria = Auditoria(
            entidad=entidad,
            entidad_id=entidad_id,
            accion=accion,
            usuario_id=usuario_id,
            valores_anteriores=anteriores,
            valores_nuevos=nuevos,
        )
        self.db.add(auditoria)

    def _obtener_usuario_actual(self, usuario_id: int) -> User:
        usuario_actual = self.db.query(User).filter(User.id == usuario_id).first()

        if not usuario_actual:
            raise HTTPException(status_code=401, detail="Usuario autenticado no encontrado")

        return usuario_actual

    def _es_super_admin(self, usuario: User) -> bool:
        return usuario.role == "super_admin"

    def _validar_super_admin_activo_minimo(self, usuario: User):
        """
        Evita dejar el sistema sin ningún Super Admin activo.
        """
        if usuario.role != "super_admin":
            return

        total_super_admin_activos = (
            self.db.query(User)
            .filter(
                User.role == "super_admin",
                User.activo == True,
            )
            .count()
        )

        if total_super_admin_activos <= 1:
            raise HTTPException(
                status_code=400,
                detail="No puedes desactivar o modificar al último Super Admin activo",
            )

    def _validar_accion_sobre_super_admin(self, usuario_objetivo: User, usuario_actual: User):
        """
        Un usuario que no sea Super Admin no puede modificar, activar,
        desactivar ni cambiar el rol de un Super Admin.
        """
        if usuario_objetivo.role == "super_admin" and not self._es_super_admin(usuario_actual):
            raise HTTPException(
                status_code=403,
                detail="Solo un Super Admin puede modificar a otro Super Admin",
            )

    def listar_permisos(self):
        return (
            self.db.query(Permiso)
            .filter(Permiso.activo == True)
            .order_by(Permiso.modulo, Permiso.codigo)
            .all()
        )

    def listar_roles(self):
        return (
            self.db.query(Rol)
            .filter(Rol.activo == True)
            .order_by(Rol.id)
            .all()
        )

    def obtener_rol_por_codigo(self, codigo: str):
        return (
            self.db.query(Rol)
            .filter(
                Rol.codigo == codigo,
                Rol.activo == True,
            )
            .first()
        )

    def obtener_rol(self, rol_id: int):
        rol = (
            self.db.query(Rol)
            .filter(
                Rol.id == rol_id,
                Rol.activo == True,
            )
            .first()
        )

        if not rol:
            raise HTTPException(status_code=404, detail="Rol no encontrado")

        return rol

    def _sync_permisos(self, rol: Rol, permisos_codigos: list[str]):
        self.db.query(RolPermiso).filter(RolPermiso.rol_id == rol.id).delete()

        permisos = (
            self.db.query(Permiso)
            .filter(Permiso.codigo.in_(permisos_codigos))
            .all()
        )

        for permiso in permisos:
            self.db.add(
                RolPermiso(
                    rol_id=rol.id,
                    permiso_id=permiso.id,
                )
            )

    def crear_rol(self, data: RolCreate, usuario_id: int):
        usuario_actual = self._obtener_usuario_actual(usuario_id)

        if not self._es_super_admin(usuario_actual):
            raise HTTPException(
                status_code=403,
                detail="Solo un Super Admin puede crear roles personalizados",
            )

        if data.codigo in ["super_admin", "admin", "editor_sitios", "gestor_contenido", "gestor_tienda", "auditor", "user"]:
            raise HTTPException(
                status_code=400,
                detail="No puedes crear un rol personalizado usando un código reservado del sistema",
            )

        existente = self.db.query(Rol).filter(Rol.codigo == data.codigo).first()

        if existente:
            raise HTTPException(status_code=400, detail="Ya existe un rol con ese código")

        rol = Rol(
            nombre=data.nombre,
            codigo=data.codigo,
            descripcion=data.descripcion,
            activo=True,
            es_sistema=False,
        )

        self.db.add(rol)
        self.db.flush()

        self._sync_permisos(rol, data.permisos)

        self._auditar(
            entidad="roles",
            entidad_id=rol.id,
            accion="INSERT",
            usuario_id=usuario_id,
            anteriores=None,
            nuevos={
                "nombre": rol.nombre,
                "codigo": rol.codigo,
                "permisos": data.permisos,
            },
        )

        self.db.commit()
        self.db.refresh(rol)

        return rol

    def actualizar_rol(self, rol_id: int, data: RolUpdate, usuario_id: int):
        usuario_actual = self._obtener_usuario_actual(usuario_id)

        if not self._es_super_admin(usuario_actual):
            raise HTTPException(
                status_code=403,
                detail="Solo un Super Admin puede editar roles",
            )

        rol = self.obtener_rol(rol_id)

        if rol.es_sistema:
            raise HTTPException(
                status_code=400,
                detail="No se puede editar un rol del sistema",
            )

        anteriores = {
            "nombre": rol.nombre,
            "codigo": rol.codigo,
            "descripcion": rol.descripcion,
            "activo": rol.activo,
            "permisos": [
                rp.permiso.codigo
                for rp in rol.permisos
                if rp.permiso is not None
            ],
        }

        if data.nombre is not None:
            rol.nombre = data.nombre

        if data.descripcion is not None:
            rol.descripcion = data.descripcion

        if data.activo is not None:
            rol.activo = data.activo

        if data.permisos is not None:
            self._sync_permisos(rol, data.permisos)

        nuevos = {
            "nombre": rol.nombre,
            "codigo": rol.codigo,
            "descripcion": rol.descripcion,
            "activo": rol.activo,
            "permisos": data.permisos if data.permisos is not None else anteriores["permisos"],
        }

        self._auditar(
            entidad="roles",
            entidad_id=rol.id,
            accion="UPDATE",
            usuario_id=usuario_id,
            anteriores=anteriores,
            nuevos=nuevos,
        )

        self.db.commit()
        self.db.refresh(rol)

        return rol

    def eliminar_rol(self, rol_id: int, usuario_id: int):
        usuario_actual = self._obtener_usuario_actual(usuario_id)

        if not self._es_super_admin(usuario_actual):
            raise HTTPException(
                status_code=403,
                detail="Solo un Super Admin puede eliminar roles",
            )

        rol = self.obtener_rol(rol_id)

        if rol.es_sistema:
            raise HTTPException(
                status_code=400,
                detail="No se puede eliminar un rol del sistema",
            )

        usuarios_con_rol = self.db.query(User).filter(User.role == rol.codigo).count()

        if usuarios_con_rol > 0:
            raise HTTPException(
                status_code=400,
                detail="No puedes eliminar este rol porque tiene usuarios asignados",
            )

        anteriores = jsonable_encoder(rol)

        rol.activo = False

        self._auditar(
            entidad="roles",
            entidad_id=rol.id,
            accion="DELETE",
            usuario_id=usuario_id,
            anteriores=anteriores,
            nuevos={"activo": False},
        )

        self.db.commit()

        return {"mensaje": "Rol desactivado correctamente"}

    def listar_usuarios(self):
        return self.db.query(User).order_by(User.id).all()

    def crear_usuario_sistema(self, data: UsuarioSistemaCreate, usuario_id: int):
        usuario_actual = self._obtener_usuario_actual(usuario_id)

        if data.role == "super_admin" and not self._es_super_admin(usuario_actual):
            raise HTTPException(
                status_code=403,
                detail="Solo un Super Admin puede crear otro Super Admin",
            )

        rol = self.obtener_rol_por_codigo(data.role)

        if not rol:
            raise HTTPException(status_code=400, detail="Rol no válido")

        existente = self.db.query(User).filter(User.correo == data.correo).first()

        if existente:
            raise HTTPException(status_code=400, detail="El correo ya está registrado")

        nuevo_usuario = User(
            correo=data.correo,
            contrasena=get_password_hash(data.contrasena),
            nombre=data.nombre,
            apellido=data.apellido,
            role=data.role,
            activo=True,
        )

        self.db.add(nuevo_usuario)
        self.db.flush()

        valores_nuevos = jsonable_encoder(nuevo_usuario)
        valores_nuevos.pop("contrasena", None)

        self._auditar(
            entidad="users",
            entidad_id=nuevo_usuario.id,
            accion="INSERT",
            usuario_id=usuario_id,
            anteriores=None,
            nuevos=valores_nuevos,
        )

        self.db.commit()
        self.db.refresh(nuevo_usuario)

        return nuevo_usuario

    def cambiar_rol_usuario(self, user_id: int, nuevo_role: str, usuario_id: int):
        usuario_actual = self._obtener_usuario_actual(usuario_id)

        usuario = self.db.query(User).filter(User.id == user_id).first()

        if not usuario:
            raise HTTPException(status_code=404, detail=USUARIO_NO_ENCONTRADO)

        if usuario.id == usuario_id and usuario.role == "super_admin" and nuevo_role != "super_admin":
            raise HTTPException(
                status_code=400,
                detail="No puedes quitarte a ti mismo el rol Super Admin",
            )

        self._validar_accion_sobre_super_admin(usuario, usuario_actual)

        if nuevo_role == "super_admin" and not self._es_super_admin(usuario_actual):
            raise HTTPException(
                status_code=403,
                detail="Solo un Super Admin puede asignar el rol Super Admin",
            )

        if usuario.role == "super_admin" and nuevo_role != "super_admin":
            self._validar_super_admin_activo_minimo(usuario)

        rol = self.obtener_rol_por_codigo(nuevo_role)

        if not rol:
            raise HTTPException(status_code=400, detail="Rol no válido")

        anteriores = {
            "id": usuario.id,
            "correo": usuario.correo,
            "role": usuario.role,
        }

        usuario.role = nuevo_role

        nuevos = {
            "id": usuario.id,
            "correo": usuario.correo,
            "role": usuario.role,
        }

        self._auditar(
            entidad="users",
            entidad_id=usuario.id,
            accion="UPDATE",
            usuario_id=usuario_id,
            anteriores=anteriores,
            nuevos=nuevos,
        )

        self.db.commit()
        self.db.refresh(usuario)

        return usuario

    def desactivar_usuario(self, user_id: int, usuario_id: int):
        usuario_actual = self._obtener_usuario_actual(usuario_id)

        usuario = self.db.query(User).filter(User.id == user_id).first()

        if not usuario:
            raise HTTPException(status_code=404, detail=USUARIO_NO_ENCONTRADO)

        if usuario.id == usuario_id:
            raise HTTPException(
                status_code=400,
                detail="No puedes desactivar tu propia cuenta",
            )

        self._validar_accion_sobre_super_admin(usuario, usuario_actual)

        if usuario.role == "super_admin":
            self._validar_super_admin_activo_minimo(usuario)

        anteriores = {
            "id": usuario.id,
            "correo": usuario.correo,
            "activo": usuario.activo,
        }

        usuario.activo = False

        self._auditar(
            entidad="users",
            entidad_id=usuario.id,
            accion="DELETE",
            usuario_id=usuario_id,
            anteriores=anteriores,
            nuevos={"activo": False},
        )

        self.db.commit()

        return {"mensaje": "Usuario desactivado correctamente"}

    def activar_usuario(self, user_id: int, usuario_id: int):
        usuario_actual = self._obtener_usuario_actual(usuario_id)

        usuario = self.db.query(User).filter(User.id == user_id).first()

        if not usuario:
            raise HTTPException(status_code=404, detail=USUARIO_NO_ENCONTRADO)

        self._validar_accion_sobre_super_admin(usuario, usuario_actual)

        anteriores = {
            "id": usuario.id,
            "correo": usuario.correo,
            "activo": usuario.activo,
        }

        usuario.activo = True

        self._auditar(
            entidad="users",
            entidad_id=usuario.id,
            accion="UPDATE",
            usuario_id=usuario_id,
            anteriores=anteriores,
            nuevos={"activo": True},
        )

        self.db.commit()
        self.db.refresh(usuario)

        return usuario

    def obtener_permisos_usuario(self, usuario: User):
        if usuario.role == "super_admin":
            permisos = (
                self.db.query(Permiso)
                .filter(Permiso.activo == True)
                .all()
            )
            return [p.codigo for p in permisos]

        rol = (
            self.db.query(Rol)
            .filter(
                Rol.codigo == usuario.role,
                Rol.activo == True,
            )
            .first()
        )

        if not rol:
            return []

        permisos = (
            self.db.query(Permiso)
            .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
            .filter(
                RolPermiso.rol_id == rol.id,
                Permiso.activo == True,
            )
            .all()
        )

        return [p.codigo for p in permisos]