# Roles y permisos

El backend utiliza un enfoque de control de acceso basado en roles y permisos. Esto permite que las acciones del sistema no dependan solamente de si el usuario inició sesión, sino también de qué permisos tiene asignados.

## Componentes del modelo RBAC

| Componente | Descripción |
|---|---|
| Rol | Agrupa responsabilidades del usuario. |
| Permiso | Representa una acción específica autorizable. |
| Rol-Permiso | Relación que asigna permisos a roles. |
| Usuario | Cuenta que puede tener rol asignado. |

## Ejemplos de permisos por módulo

| Módulo | Permisos esperados |
|---|---|
| Blog | `blog.ver`, `blog.crear`, `blog.editar`, `blog.eliminar` |
| Tienda | `tienda.ver`, `tienda.crear`, `tienda.editar`, `tienda.eliminar` |
| Analítica | `analitica.ver`, `analitica.crear` |
| Sitios | permisos de administración de sitio. |
| Roles | permisos para gestionar usuarios y roles. |

## Dependencia de autorización

Las rutas críticas pueden usar dependencias como `require_permission(...)`. Esto centraliza la validación y reduce el riesgo de repetir lógica de seguridad manualmente en cada endpoint.

```python
current_user: User = Depends(require_permission("blog.ver"))
```

## Ventajas

- permite granularidad por acción;
- facilita separar perfiles administrativos;
- mejora trazabilidad de autorizaciones;
- ayuda a cumplir criterios de seguridad del SDLC;
- evita que todo usuario autenticado tenga acceso completo.

## Puntos a revisar

- que todas las operaciones críticas tengan permiso;
- que los permisos estén sembrados o documentados;
- que roles de sistema no se modifiquen indebidamente;
- que el frontend no sea el único filtro de seguridad;
- que el backend siempre aplique la autorización real.

<div class="decision-box" markdown>
**Idea clave:** el control de permisos debe estar en el backend; el frontend puede ocultar botones, pero la autorización real se valida en la API.
</div>
