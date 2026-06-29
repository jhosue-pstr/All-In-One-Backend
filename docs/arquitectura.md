# Arquitectura backend

El backend de All-InOne utiliza una arquitectura de **Monolito Modular**.

## Componentes principales

- Autenticación interna
- Gestión de usuarios
- Roles y permisos
- Sitios / tenants
- Plantillas
- Módulos activables
- Blog
- Tienda
- Auth Público
- Analítica
- Auditoría
- Soft delete

## Enfoque multitenant

La información se asocia a cada sitio o tenant para evitar accesos cruzados entre negocios.