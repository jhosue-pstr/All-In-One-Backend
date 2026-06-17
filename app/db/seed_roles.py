from sqlalchemy.orm import Session

from app.models.rol import Rol, Permiso, RolPermiso


# Permisos - Inicio
PERM_INICIO_VER = "inicio.ver"

# Permisos - Sitios
PERM_SITIOS_VER = "sitios.ver"
PERM_SITIOS_CREAR = "sitios.crear"
PERM_SITIOS_EDITAR = "sitios.editar"
PERM_SITIOS_ELIMINAR = "sitios.eliminar"

# Permisos - Plantillas
PERM_PLANTILLAS_VER = "plantillas.ver"
PERM_PLANTILLAS_CREAR = "plantillas.crear"
PERM_PLANTILLAS_EDITAR = "plantillas.editar"
PERM_PLANTILLAS_ELIMINAR = "plantillas.eliminar"

# Permisos - Módulos
PERM_MODULOS_VER = "modulos.ver"
PERM_MODULOS_CREAR = "modulos.crear"
PERM_MODULOS_EDITAR = "modulos.editar"
PERM_MODULOS_ELIMINAR = "modulos.eliminar"
PERM_MODULOS_ACTIVAR = "modulos.activar"

# Permisos - Blog
PERM_BLOG_VER = "blog.ver"
PERM_BLOG_CREAR = "blog.crear"
PERM_BLOG_EDITAR = "blog.editar"
PERM_BLOG_ELIMINAR = "blog.eliminar"

# Permisos - Tienda
PERM_TIENDA_VER = "tienda.ver"
PERM_TIENDA_CREAR = "tienda.crear"
PERM_TIENDA_EDITAR = "tienda.editar"
PERM_TIENDA_ELIMINAR = "tienda.eliminar"
PERM_TIENDA_PEDIDOS = "tienda.pedidos"

# Permisos - Configuraciones
PERM_CONFIGURACIONES_VER = "configuraciones.ver"
PERM_CONFIGURACIONES_EDITAR = "configuraciones.editar"

# Permisos - Roles
PERM_ROLES_VER = "roles.ver"
PERM_ROLES_CREAR = "roles.crear"
PERM_ROLES_EDITAR = "roles.editar"
PERM_ROLES_ELIMINAR = "roles.eliminar"
PERM_ROLES_USUARIOS = "roles.usuarios"

# Permisos - Auditoría
PERM_AUDITORIA_VER = "auditoria.ver"

# Permisos - Analítica
PERM_ANALITICA_VER = "analitica.ver"
PERM_ANALITICA_CREAR = "analitica.crear"


PERMISOS_BASE = [
    # Inicio
    (PERM_INICIO_VER, "Ver Inicio", "inicio"),

    # Sitios
    (PERM_SITIOS_VER, "Ver sitios", "sitios"),
    (PERM_SITIOS_CREAR, "Crear sitios", "sitios"),
    (PERM_SITIOS_EDITAR, "Editar sitios", "sitios"),
    (PERM_SITIOS_ELIMINAR, "Eliminar sitios", "sitios"),

    # Plantillas
    (PERM_PLANTILLAS_VER, "Ver plantillas", "plantillas"),
    (PERM_PLANTILLAS_CREAR, "Crear plantillas", "plantillas"),
    (PERM_PLANTILLAS_EDITAR, "Editar plantillas", "plantillas"),
    (PERM_PLANTILLAS_ELIMINAR, "Eliminar plantillas", "plantillas"),

    # Módulos
    (PERM_MODULOS_VER, "Ver módulos", "modulos"),
    (PERM_MODULOS_CREAR, "Crear módulos", "modulos"),
    (PERM_MODULOS_EDITAR, "Editar módulos", "modulos"),
    (PERM_MODULOS_ELIMINAR, "Eliminar módulos", "modulos"),
    (PERM_MODULOS_ACTIVAR, "Activar o desactivar módulos", "modulos"),

    # Blog
    (PERM_BLOG_VER, "Ver blog", "blog"),
    (PERM_BLOG_CREAR, "Crear publicaciones", "blog"),
    (PERM_BLOG_EDITAR, "Editar publicaciones", "blog"),
    (PERM_BLOG_ELIMINAR, "Eliminar publicaciones", "blog"),

    # Tienda
    (PERM_TIENDA_VER, "Ver tienda", "tienda"),
    (PERM_TIENDA_CREAR, "Crear productos o categorías", "tienda"),
    (PERM_TIENDA_EDITAR, "Editar productos o categorías", "tienda"),
    (PERM_TIENDA_ELIMINAR, "Eliminar productos o categorías", "tienda"),
    (PERM_TIENDA_PEDIDOS, "Gestionar pedidos", "tienda"),

    # Configuraciones
    (PERM_CONFIGURACIONES_VER, "Ver configuraciones", "configuraciones"),
    (PERM_CONFIGURACIONES_EDITAR, "Editar configuraciones", "configuraciones"),

    # Roles
    (PERM_ROLES_VER, "Ver roles", "roles"),
    (PERM_ROLES_CREAR, "Crear roles", "roles"),
    (PERM_ROLES_EDITAR, "Editar roles", "roles"),
    (PERM_ROLES_ELIMINAR, "Eliminar roles", "roles"),
    (PERM_ROLES_USUARIOS, "Gestionar usuarios del sistema", "roles"),

    # Auditoría
    (PERM_AUDITORIA_VER, "Ver auditoría", "auditoria"),

    # Analítica
    (PERM_ANALITICA_VER, "Ver analítica", "analitica"),
    (PERM_ANALITICA_CREAR, "Crear eventos de analítica", "analitica"),
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
            PERM_INICIO_VER,
            PERM_SITIOS_VER,
            PERM_SITIOS_CREAR,
            PERM_SITIOS_EDITAR,
            PERM_PLANTILLAS_VER,
            PERM_PLANTILLAS_CREAR,
            PERM_PLANTILLAS_EDITAR,
            PERM_MODULOS_VER,
            PERM_MODULOS_ACTIVAR,
            PERM_BLOG_VER,
            PERM_BLOG_CREAR,
            PERM_BLOG_EDITAR,
            PERM_BLOG_ELIMINAR,
            PERM_TIENDA_VER,
            PERM_TIENDA_CREAR,
            PERM_TIENDA_EDITAR,
            PERM_TIENDA_ELIMINAR,
            PERM_TIENDA_PEDIDOS,
            PERM_CONFIGURACIONES_VER,
            PERM_ROLES_VER,
            PERM_ROLES_USUARIOS,
            PERM_AUDITORIA_VER,
            PERM_ANALITICA_VER,
        ],
    },
    "editor_sitios": {
        "nombre": "Editor de Sitios",
        "descripcion": "Puede editar sitios y plantillas, pero no gestionar módulos críticos.",
        "permisos": [
            PERM_INICIO_VER,
            PERM_SITIOS_VER,
            PERM_SITIOS_EDITAR,
            PERM_PLANTILLAS_VER,
            PERM_PLANTILLAS_EDITAR,
            PERM_MODULOS_VER,
            PERM_BLOG_VER,
            PERM_BLOG_EDITAR,
        ],
    },
    "gestor_contenido": {
        "nombre": "Gestor de Contenido",
        "descripcion": "Gestiona publicaciones, noticias e imágenes del blog.",
        "permisos": [
            PERM_INICIO_VER,
            PERM_SITIOS_VER,
            PERM_MODULOS_VER,
            PERM_BLOG_VER,
            PERM_BLOG_CREAR,
            PERM_BLOG_EDITAR,
            PERM_BLOG_ELIMINAR,
        ],
    },
    "gestor_tienda": {
        "nombre": "Gestor de Tienda",
        "descripcion": "Gestiona productos, categorías y pedidos.",
        "permisos": [
            PERM_INICIO_VER,
            PERM_SITIOS_VER,
            PERM_MODULOS_VER,
            PERM_TIENDA_VER,
            PERM_TIENDA_CREAR,
            PERM_TIENDA_EDITAR,
            PERM_TIENDA_ELIMINAR,
            PERM_TIENDA_PEDIDOS,
        ],
    },
    "auditor": {
        "nombre": "Solo Lectura / Auditor",
        "descripcion": "Solo puede visualizar información y revisar auditoría.",
        "permisos": [
            PERM_INICIO_VER,
            PERM_SITIOS_VER,
            PERM_PLANTILLAS_VER,
            PERM_MODULOS_VER,
            PERM_BLOG_VER,
            PERM_TIENDA_VER,
            PERM_CONFIGURACIONES_VER,
            PERM_AUDITORIA_VER,
            PERM_ANALITICA_VER,
        ],
    },
    "user": {
        "nombre": "Usuario Básico",
        "descripcion": "Rol básico para compatibilidad con usuarios antiguos.",
        "permisos": [
            PERM_INICIO_VER,
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
                    db.add(
                        RolPermiso(
                            rol_id=rol.id,
                            permiso_id=permiso.id,
                        )
                    )

    db.commit()