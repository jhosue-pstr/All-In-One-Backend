# Resumen de endpoints

La API del backend se documenta mediante Swagger/OpenAPI.

## Grupos funcionales esperados

- Autenticación.
- Usuarios.
- Roles y permisos.
- Sitios.
- Plantillas.
- Módulos.
- Blog.
- Tienda.
- Auth Público.
- Analítica.

## Validaciones relevantes

Cada endpoint crítico debe revisarse considerando:

- Autenticación JWT.
- Permisos por rol.
- Aislamiento por tenant.
- Validación de datos.
- Manejo de errores.
- Registro de acciones relevantes.
