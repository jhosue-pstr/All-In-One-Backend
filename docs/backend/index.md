# Documentación del Backend

Esta sección describe la parte servidor de All-InOne: arquitectura, módulos, API, seguridad, pruebas, calidad y despliegue técnico.

## Enfoque del backend

El backend se construye con **FastAPI en Python**, persistencia mediante **SQLAlchemy**, autenticación mediante **JWT**, control de acceso por **roles y permisos**, y organización por dominios funcionales dentro de una arquitectura de **monolito modular**.

## Componentes principales

<div class="section-grid" markdown>

<div class="section-card" markdown>
### Core y sitios
Gestión de tenants, sitios, plantillas y módulos activables.
</div>

<div class="section-card" markdown>
### Seguridad
JWT, RBAC, protección de endpoints, roles, permisos y separación por tenant.
</div>

<div class="section-card" markdown>
### Módulos de negocio
Blog, Tienda, Auth Público, Analítica y componentes transversales.
</div>

<div class="section-card" markdown>
### Controles transversales
Auditoría de acciones relevantes y soft delete para preservación de registros.
</div>

</div>

## Relación con auditoría

La documentación backend sirve como evidencia para varios objetivos de auditoría: diseño, construcción, seguridad, pruebas, calidad, mantenimiento y trazabilidad.
