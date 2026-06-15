from sqlalchemy.orm import Session

from app.models.rol import Rol, Permiso, RolPermiso


PERMISOS_BASE = [
    # Inicio
    ("inicio.ver", "Ver Inicio", "inicio"),

    # Sitios
    ("sitios.ver", "Ver sitios", "sitios"),
    ("sitios.crear", "Crear sitios", "sitios"),
    ("sitios.editar", "Editar sitios", "sitios"),
    ("sitios.eliminar", "Eliminar sitios", "sitios"),

    # Plantillas
    ("plantillas.ver", "Ver plantillas", "plantillas"),
    ("plantillas.crear", "Crear plantillas", "plantillas"),
    ("plantillas.editar", "Editar plantillas", "plantillas"),
    ("plantillas.eliminar", "Eliminar plantillas", "plantillas"),

    # Módulos
    ("modulos.ver", "Ver módulos", "modulos"),
    ("modulos.crear", "Crear módulos", "modulos"),
    ("modulos.editar", "Editar módulos", "modulos"),
    ("modulos.eliminar", "Eliminar módulos", "modulos"),
    ("modulos.activar", "Activar o desactivar módulos", "modulos"),

    # Blog
    ("blog.ver", "Ver blog", "blog"),
    ("blog.crear", "Crear publicaciones", "blog"),
    ("blog.editar", "Editar publicaciones", "blog"),
    ("blog.eliminar", "Eliminar publicaciones", "blog"),

    # Tienda
    ("tienda.ver", "Ver tienda", "tienda"),
    ("tienda.crear", "Crear productos o categorías", "tienda"),
    ("tienda.editar", "Editar productos o categorías", "tienda"),
    ("tienda.eliminar", "Eliminar productos o categorías", "tienda"),
    ("tienda.pedidos", "Gestionar pedidos", "tienda"),

    # Configuraciones
    ("configuraciones.ver", "Ver configuraciones", "configuraciones"),
    ("configuraciones.editar", "Editar configuraciones", "configuraciones"),

    # Roles
    ("roles.ver", "Ver roles", "roles"),
    ("roles.crear", "Crear roles", "roles"),
    ("roles.editar", "Editar roles", "roles"),
    ("roles.eliminar", "Eliminar roles", "roles"),
    ("roles.usuarios", "Gestionar usuarios del sistema", "roles"),

    # Auditoría
    ("auditoria.ver", "Ver auditoría", "auditoria"),
]


ROLES_BASE = {
    "super_admin": {
        "nombre": "Super Admin",
        "descripcion": "Cuenta con acceso total al sistema.",
        "permisos": [codigo for codigo, _, _ in PERMISOS_BASE],
    },
    "admin": {
        "nombre": "Administrador",
        "descripcion": "Administra el sistema sin control total de permisos críticos.",
        "permisos": [
            "inicio.ver",
            "sitios.ver", "sitios.crear", "sitios.editar",
            "plantillas.ver", "plantillas.crear", "plantillas.editar",
            "modulos.ver", "modulos.activar",
            "blog.ver", "blog.crear", "blog.editar", "blog.eliminar",
            "tienda.ver", "tienda.crear", "tienda.editar", "tienda.eliminar", "tienda.pedidos",
            "configuraciones.ver",
            "roles.ver", "roles.usuarios",
            "auditoria.ver",
        ],
    },
    "editor_sitios": {
        "nombre": "Editor de Sitios",
        "descripcion": "Puede editar sitios y plantillas, pero no gestionar módulos críticos.",
        "permisos": [
            "inicio.ver",
            "sitios.ver", "sitios.editar",
            "plantillas.ver", "plantillas.editar",
            "modulos.ver",
            "blog.ver", "blog.editar",
        ],
    },
    "gestor_contenido": {
        "nombre": "Gestor de Contenido",
        "descripcion": "Gestiona publicaciones, noticias e imágenes del blog.",
        "permisos": [
            "inicio.ver",
            "sitios.ver",
            "modulos.ver",
            "blog.ver", "blog.crear", "blog.editar", "blog.eliminar",
        ],
    },
    "gestor_tienda": {
        "nombre": "Gestor de Tienda",
        "descripcion": "Gestiona productos, categorías y pedidos.",
        "permisos": [
            "inicio.ver",
            "sitios.ver",
            "modulos.ver",
            "tienda.ver", "tienda.crear", "tienda.editar", "tienda.eliminar", "tienda.pedidos",
        ],
    },
    "auditor": {
        "nombre": "Solo Lectura / Auditor",
        "descripcion": "Solo puede visualizar información y revisar auditoría.",
        "permisos": [
            "inicio.ver",
            "sitios.ver",
            "plantillas.ver",
            "modulos.ver",
            "blog.ver",
            "tienda.ver",
            "configuraciones.ver",
            "auditoria.ver",
        ],
    },
    "user": {
        "nombre": "Usuario Básico",
        "descripcion": "Rol básico para compatibilidad con usuarios antiguos.",
        "permisos": [
            "inicio.ver",
        ],
    },
}


def seed_roles(db: Session):
    permisos_map = {}

    for codigo, nombre, modulo in PERMISOS_BASE:
        permiso = db.query(Permiso).filter(Permiso.codigo == codigo).first()

        if not permiso:
            permiso = Permiso(
                codigo=codigo,
                nombre=nombre,
                modulo=modulo,
                descripcion=nombre,
                activo=True,
            )
            db.add(permiso)
            db.flush()

        permisos_map[codigo] = permiso

    for codigo_rol, data in ROLES_BASE.items():
        rol = db.query(Rol).filter(Rol.codigo == codigo_rol).first()

        if not rol:
            rol = Rol(
                codigo=codigo_rol,
                nombre=data["nombre"],
                descripcion=data["descripcion"],
                activo=True,
                es_sistema=True,
            )
            db.add(rol)
            db.flush()

        permisos_actuales = {
            rp.permiso.codigo
            for rp in rol.permisos
            if rp.permiso is not None
        }

        for permiso_codigo in data["permisos"]:
            if permiso_codigo not in permisos_actuales:
                permiso = permisos_map.get(permiso_codigo)
                if permiso:
                    db.add(RolPermiso(rol_id=rol.id, permiso_id=permiso.id))

    db.commit()