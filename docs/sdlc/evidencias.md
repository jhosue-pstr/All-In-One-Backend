# Evidencias del backend para auditoría SDLC

Esta sección resume los artefactos del backend que pueden utilizarse como evidencia de auditoría.

## Evidencias por fase SDLC

| Fase SDLC | Evidencia del backend |
|---|---|
| Requisitos | Historias, criterios y módulos documentados en Jira e informe del proyecto. |
| Diseño | Arquitectura de monolito modular, estructura por capas y módulos. |
| Construcción | Código fuente en `app/`, modelos, servicios, rutas y esquemas. |
| Pruebas | Carpeta `test/`, Pytest, k6, ZAP y reportes de calidad. |
| Implementación | Dockerfile, Jenkinsfile, Swagger, despliegue de prueba. |
| Seguridad | JWT, RBAC, multitenancy, ZAP, Snyk, auditoría y soft delete. |
| Mantenimiento | Modularidad, separación de responsabilidades y control de versiones. |
| Documentación | MkDocs, README, Swagger/OpenAPI y documentos del proyecto. |

## Evidencias técnicas principales

- `app/main.py`
- `app/api/`
- `app/models/`
- `app/schemas/`
- `app/service/`
- `app/packages/modulos/`
- `test/`
- `k6/`
- `zap/`
- `Jenkinsfile`
- `Dockerfile`
- `pytest.ini`
- `requirements.txt`

## Uso en auditoría

Estas evidencias permiten contrastar lo documentado con lo implementado, identificando conformidades, brechas y oportunidades de mejora.
