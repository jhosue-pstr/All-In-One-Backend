# Checklist SDLC

El **Checklist SDLC** es el instrumento operativo de verificación de la auditoría. Permite revisar de forma ordenada si el proyecto cuenta con evidencias suficientes para cada objetivo de control.

## Criterio de marcado

En el checklist se marca:

- **Cumple**, cuando existe evidencia suficiente.
- **No cumple**, cuando no existe evidencia formal suficiente o el proyecto no llegó a ese nivel de formalidad.

!!! note "Criterio conservador"
    No se marca todo como cumple. En auditoría es mejor reconocer brechas reales y explicar por qué no aplican o no se evidencian completamente.

## Bloques evaluados

| Bloque | Evaluación general |
|---|---|
| Metodología SDLC | Cumple en planificación, alcance, entregables y riesgos; no cumple en autorizaciones por fase ni herramientas CASE |
| Análisis de necesidades | Cumple en requisitos, historias, Jira y trazabilidad; no cumple en análisis costo/beneficio formal por necesidad |
| Diseño y desarrollo | Cumple en arquitectura, controles, GitHub y CI/CD de prueba; no cumple en aprobación formal de diseño y wiki de codificación |
| Procedimientos de prueba | Cumple por evidencias de pruebas funcionales, E2E, rendimiento, seguridad y calidad |
| Implementación | No cumple como implementación productiva formal; solo existe despliegue académico/de prueba |
| Revisión post-implementación | No cumple porque no hubo operación real posterior a producción |
| Mantenimiento | No cumple como mantenimiento formal post-producción; sí existe modularidad y componentes reutilizables |
| Software de sistema | No cumple porque no se modificó ni homologó software base, compiladores o herramientas CASE |
| Documentación | Cumple en documentación técnica general; algunas brechas dependen de estándares formales de difusión |

## Relación con MkDocs

MkDocs fortalece la evidencia documental porque organiza la información técnica del backend y frontend, además de la sección de auditoría SDLC.

Sin embargo, MkDocs no reemplaza:

- autorizaciones formales;
- herramientas CASE;
- implementación productiva formal;
- mantenimiento post-producción;
- certificaciones oficiales.

## Idea clave

El checklist demuestra que el proyecto tiene fortalezas en planificación, desarrollo, pruebas, seguridad y documentación, pero también reconoce límites propios de un proyecto académico sin producción empresarial formal.
