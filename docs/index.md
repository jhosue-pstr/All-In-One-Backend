# All-InOne Backend

Bienvenido a la documentación técnica del **backend de All-InOne**, una plataforma SaaS multitenant desarrollada por **ModularSoft - Grupo 4**.

Esta documentación tiene como finalidad explicar de forma ordenada la estructura, arquitectura, API, seguridad, pruebas, calidad y despliegue de prueba del backend.

!!! info "Alcance de esta documentación"
    Esta documentación describe el backend como parte de un proyecto académico. El sistema cuenta con despliegue y evidencias técnicas de prueba, pero no representa una implementación productiva formal para una empresa real.

## Propósito del backend

El backend es responsable de exponer los servicios principales de All-InOne mediante una API construida con **FastAPI**. Desde esta capa se gestionan los usuarios, roles, permisos, sitios, plantillas, módulos activables, blog, tienda, autenticación pública, analítica, auditoría y eliminación lógica.

## Tecnologías principales

| Tecnología | Uso dentro del backend |
|---|---|
| FastAPI | Construcción de API REST |
| Python | Lenguaje principal del backend |
| SQLAlchemy | Acceso y persistencia de datos |
| JWT | Autenticación mediante tokens |
| RBAC | Control de acceso basado en roles y permisos |
| Swagger/OpenAPI | Documentación automática de endpoints |
| Pytest | Pruebas automatizadas del backend |
| k6 | Pruebas de rendimiento |
| OWASP ZAP | Pruebas de seguridad dinámicas |
| Jenkins | Integración continua y ejecución de tareas automatizadas |

## Componentes funcionales

- Autenticación interna.
- Gestión de usuarios del sistema.
- Gestión de roles y permisos.
- Gestión de sitios o tenants.
- Gestión de plantillas.
- Activación y desactivación de módulos por sitio.
- Módulo Blog.
- Módulo Tienda.
- Módulo Auth Público.
- Módulo Analítica.
- Auditoría de operaciones relevantes.
- Soft delete para preservar registros importantes.

## Lectura recomendada

Para entender el proyecto rápidamente, revisar en este orden:

1. [Instalación local](instalacion.md)
2. [Visión general de arquitectura](arquitectura/vision-general.md)
3. [Resumen de endpoints](api/resumen-endpoints.md)
4. [Controles de seguridad](seguridad/controles.md)
5. [Estrategia de pruebas](pruebas/estrategia.md)
6. [Limitaciones SDLC](sdlc/limitaciones.md)
