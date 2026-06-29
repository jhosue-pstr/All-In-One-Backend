# Roles y permisos

All-InOne utiliza control de acceso basado en roles y permisos para limitar las acciones de los usuarios internos.

## Prefijo relacionado

```text
/api/roles
```

## Endpoints principales

| Método | Ruta | Función |
|---|---|---|
| GET | `/api/roles/mis-permisos` | Obtiene permisos del usuario autenticado. |
| GET | `/api/roles/permisos` | Lista permisos disponibles. |
| GET | `/api/roles` | Lista roles. |
| POST | `/api/roles` | Crea rol. |
| PUT | `/api/roles/{rol_id}` | Actualiza rol. |
| DELETE | `/api/roles/{rol_id}` | Elimina rol. |
| GET | `/api/roles/usuarios` | Lista usuarios del sistema. |
| POST | `/api/roles/usuarios` | Crea usuario interno. |
| PUT | `/api/roles/usuarios/{user_id}/rol` | Cambia rol de usuario. |
| DELETE | `/api/roles/usuarios/{user_id}` | Desactiva usuario. |
| PUT | `/api/roles/usuarios/{user_id}/activar` | Activa usuario. |

## Roles referenciales

| Rol | Descripción |
|---|---|
| Super administrador | Control amplio sobre sistema, usuarios, roles, sitios y módulos. |
| Administrador | Gestión operativa amplia, con restricciones según permisos. |
| Editor de sitios | Edición visual y configuración de sitios. |
| Gestor de contenido | Administración de publicaciones del Blog. |
| Gestor de tienda | Administración de productos, categorías y pedidos. |
| Auditor | Consulta sin modificación. |
| Usuario básico | Acceso mínimo o compatibilidad. |

## Criterio de auditoría

Para validar permisos se debe comprobar que un usuario solo pueda ejecutar acciones permitidas para su rol.
