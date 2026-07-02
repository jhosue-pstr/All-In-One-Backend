# Antecedentes de la Auditoría

Los antecedentes explican qué es **All-InOne**, cómo está construido y por qué tiene sentido auditarlo.

## Descripción del sistema

All-InOne es una plataforma SaaS multitenant orientada a pequeñas y medianas empresas. Su finalidad es permitir que una PYME pueda crear y administrar su presencia digital desde una sola plataforma.

Entre sus capacidades principales se encuentran:

- creación y administración de sitios;
- constructor visual con GrapesJS;
- gestión de plantillas;
- activación de módulos;
- Blog;
- Tienda;
- Auth Público;
- Analítica;
- usuarios, roles y permisos;
- auditoría y soft delete.

## Arquitectura y tecnología

All-InOne usa una arquitectura de **monolito modular**. Esto significa que el sistema no está separado en microservicios, pero sí organiza sus funcionalidades en módulos internos.

| Componente | Tecnología / enfoque |
|---|---|
| Backend | FastAPI, Python, SQLAlchemy |
| Frontend | React, Vite, TypeScript |
| Constructor visual | GrapesJS |
| Seguridad | JWT, roles y permisos |
| Documentación API | Swagger/OpenAPI |
| Calidad y pruebas | Jenkins, SonarCloud/SonarQube, Snyk, Playwright, k6 |

## Contexto de la auditoría

La auditoría se origina porque All-InOne tiene una complejidad técnica y documental considerable. Por ello, se necesita verificar si existe coherencia entre:

- documentación del proyecto;
- planificación en Jira;
- arquitectura declarada;
- código backend y frontend;
- reportes de pruebas;
- controles de seguridad;
- estándares de calidad.

!!! summary "Idea clave"
    Los antecedentes justifican la auditoría porque All-InOne no es una aplicación simple, sino una plataforma modular, multitenant y con varios componentes técnicos.
