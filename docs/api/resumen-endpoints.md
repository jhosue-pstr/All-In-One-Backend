# Resumen de endpoints

La API del backend se expone mediante FastAPI. La documentación interactiva puede consultarse en Swagger/OpenAPI cuando el backend está ejecutándose.

```text
http://127.0.0.1:8000/docs
```

## Endpoints base

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/` | Verificación básica de servicio. |
| GET | `/health` | Verifica el estado del backend y la conexión con base de datos. |

## Routers principales

| Grupo | Prefijo | Descripción |
|---|---|---|
| Autenticación interna | `/api/auth` | Registro, login y gestión del usuario autenticado del panel. |
| Sitios | `/api/sitios` | Gestión de sitios o tenants. |
| Módulos | `/api/modulos` | Gestión general de módulos disponibles. |
| Sitio-Módulo | `/api/sitios/{sitio_id}/modulos` | Activación o desactivación de módulos por sitio. |
| Plantillas | `/api/plantillas` | Gestión de plantillas reutilizables. |
| Roles y permisos | `/api/roles` | Gestión de roles, permisos y usuarios internos. |
| Auth Público | `/api/site-auth` | Registro/login de usuarios finales por sitio. |
| Blog | `/api/modules/blog` | Gestión de categorías y publicaciones. |
| Tienda | `/api/v1/sitios/{sitio_id}/tienda` | Gestión de productos, categorías, carrito, pedidos y checkout. |
| Analítica | `/api/modules/analitica` | Registro de visitas, eventos y métricas. |
| Renderizado público | `/{slug}` | Renderizado público de un sitio por slug. |

## Consideraciones de consumo

- Los endpoints internos requieren autenticación JWT cuando corresponda.
- Algunas acciones dependen de roles y permisos.
- Los módulos funcionales dependen del sitio o tenant.
- Los endpoints públicos deben validar el sitio correspondiente.
