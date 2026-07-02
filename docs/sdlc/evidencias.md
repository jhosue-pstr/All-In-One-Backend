# Evidencias técnicas SDLC del backend

El backend aporta evidencia directa para demostrar varias fases del ciclo de vida del desarrollo de software: diseño, construcción, pruebas, seguridad, calidad, integración y documentación.

## Mapa de evidencias

| Evidencia | Fase SDLC que sustenta |
|---|---|
| Estructura de carpetas `app/` | Diseño y construcción. |
| Modelos SQLAlchemy | Diseño de datos e implementación. |
| Schemas Pydantic | Diseño de contratos y validación. |
| Routers FastAPI | Construcción de API y documentación Swagger. |
| Servicios | Reglas de negocio y mantenibilidad. |
| Tests Pytest | Verificación y validación. |
| k6 | Pruebas de rendimiento. |
| OWASP ZAP | Revisión de seguridad. |
| Jenkinsfile | Integración continua académica/de prueba. |
| Dockerfile | Preparación de entorno ejecutable. |
| MkDocs | Documentación técnica navegable. |

## Relación con el checklist

| Bloque del checklist | Cómo ayuda el backend |
|---|---|
| CL-03 Diseño y desarrollo | Evidencia arquitectura, código modular, control de versiones y CI. |
| CL-04 Pruebas | Evidencia pruebas automatizadas, rendimiento y seguridad. |
| CL-07 Mantenimiento | Evidencia modularidad y componentes reutilizables. |
| CL-09 Documentación | Evidencia documentación técnica estructurada con MkDocs y Swagger. |

## Trazabilidad recomendada

Para defender un punto del checklist, se recomienda relacionar:

```text
Requisito / historia → módulo backend → endpoint → modelo/servicio → prueba → evidencia documental
```

Ejemplo conceptual:

```text
Gestión de Blog → app/packages/modulos/blog → routes.py → services.py/models.py → test_blog.py → MkDocs/Swagger
```

## Valor del backend como evidencia

El backend no solo muestra código fuente. También permite demostrar que existe una estructura verificable: endpoints, modelos, pruebas, configuración, herramientas de análisis y documentación.

<div class="decision-box" markdown>
**Idea clave:** el backend es una de las principales fuentes de evidencia técnica para contrastar lo planificado, documentado e implementado en All-InOne.
</div>
