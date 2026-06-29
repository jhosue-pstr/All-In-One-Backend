# Visión general de arquitectura

El backend de All-InOne utiliza una arquitectura de **Monolito Modular**. Esto significa que el sistema se ejecuta como una sola aplicación backend, pero internamente sus funcionalidades están separadas por módulos, servicios, modelos y rutas.

## Decisión arquitectónica

La arquitectura monolítica modular permite:

- Mantener una sola aplicación backend.
- Evitar la complejidad de microservicios en un proyecto académico.
- Separar responsabilidades por dominios funcionales.
- Facilitar el mantenimiento y la evolución progresiva.
- Centralizar autenticación, permisos, auditoría y persistencia.

!!! note "No es microservicios"
    El backend no está dividido en servicios independientes desplegados por separado. Los módulos viven dentro del mismo proyecto FastAPI.

## Flujo general

```text
Cliente / Frontend
      ↓
API FastAPI
      ↓
Routers por dominio
      ↓
Servicios de negocio
      ↓
Modelos SQLAlchemy
      ↓
Base de datos relacional
```

## Componentes transversales

| Componente | Propósito |
|---|---|
| JWT | Autenticar usuarios mediante tokens. |
| RBAC | Autorizar acciones según roles y permisos. |
| Multitenancy | Asociar información a un sitio o tenant. |
| Auditoría | Registrar operaciones relevantes. |
| Soft delete | Evitar eliminación física directa de registros importantes. |
| Swagger/OpenAPI | Exponer documentación técnica de endpoints. |

## Módulos principales

- Core de autenticación y usuarios.
- Sitios y tenants.
- Plantillas.
- Módulos activables.
- Blog.
- Tienda.
- Auth Público.
- Analítica.

## Ventajas para el proyecto

Esta arquitectura es adecuada para All-InOne porque permite integrar en una sola plataforma varias funcionalidades de negocio sin perder orden interno.
