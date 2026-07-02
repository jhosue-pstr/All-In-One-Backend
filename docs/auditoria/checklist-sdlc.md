# Checklist SDLC adaptado

El checklist SDLC es el instrumento operativo de verificación. Permite revisar cada área del ciclo de vida del desarrollo y marcar si existe evidencia suficiente para considerar que cumple o no cumple.

## Bloques evaluados

| Bloque | Tema | Enfoque |
|---|---|---|
| CL-01 | Metodología SDLC | Planificación, roles, alcance, entregables, riesgos y seguimiento. |
| CL-02 | Análisis de necesidades | Requisitos, historias de usuario, revisión y trazabilidad. |
| CL-03 | Diseño y desarrollo | Arquitectura, programación, controles, GitHub y CI/CD. |
| CL-04 | Procedimientos de prueba | Pruebas, calidad, defectos, automatización y revisión. |
| CL-05 | Implementación | Procedimientos formales de promoción y despliegue productivo. |
| CL-06 | Post-implementación | Revisión posterior a producción y lecciones aprendidas. |
| CL-07 | Mantenimiento | Mantenimiento formal, cambios y componentes reutilizables. |
| CL-08 | Software de sistema | Cambios en herramientas base, compiladores o software interno de sistema. |
| CL-09 | Estándares de documentación | Documentación técnica, manuales, trazabilidad y estándares. |

## Lectura general de resultados

<div class="audit-callout" markdown>

El checklist no busca que todo sea “Cumple”. Una auditoría seria también reconoce brechas. En All-InOne, varios puntos cumplen por existir evidencia documental, técnica y de pruebas; otros no cumplen porque no existe formalidad empresarial completa o porque el proyecto no llegó a una implementación productiva real.

</div>

## Resumen por bloque

| Bloque | Lectura para exposición |
|---|---|
| CL-01 Metodología | Cumple en planificación, Jira, alcance, entregables y riesgos; no cumple en autorización formal por fase ni herramientas CASE. |
| CL-02 Necesidades | Cumple en requisitos, historias de usuario y trazabilidad; no cumple en análisis costo/beneficio individual por necesidad. |
| CL-03 Diseño y desarrollo | Cumple en arquitectura, controles, GitHub, CI/CD de prueba y estándares técnicos; no cumple en aprobación formal escrita, documentos fuente y wiki de codificación. |
| CL-04 Pruebas | Cumple en estrategia, reportes, calidad, integración y defectos; no cumple en code review formal documentado. |
| CL-05 Implementación | No cumple porque no existe promoción formal a producción ni gestión formal de cambios productivos. |
| CL-06 Post-implementación | No cumple porque no hubo implementación formal en producción ni revisión posterior real. |
| CL-07 Mantenimiento | No cumple en mantenimiento formal; cumple en catálogo de componentes reutilizables. |
| CL-08 Software de sistema | No cumple porque no se evidencia modificación ni homologación formal de software de sistema. |
| CL-09 Documentación | Cumple en documentación técnica y trazabilidad; no cumple en difusión formal de cambios de estándares. |

## Regla de evaluación usada

```text
Cumple = existe evidencia suficiente y alineada al criterio.
No Cumple = no existe evidencia formal suficiente o el contexto académico no alcanza la formalidad exigida por el ítem.
```

## Casos delicados para defender

### Implementación y post-implementación

Aunque existen despliegues o ejecuciones de prueba, no existe una implementación formal en una empresa real. Por eso CL-05 y CL-06 se mantienen como **No Cumple**.

### MkDocs y documentación

MkDocs fortalece la evidencia documental porque organiza la documentación técnica y de auditoría. Sin embargo, no reemplaza autorizaciones formales, gestión formal de cambios, post-implementación ni herramientas CASE.

### Code review

GitHub y análisis estático ayudan a calidad, pero si no hay flujo formal de revisión con revisores, aprobaciones y criterios documentados, el ítem de code review formal se marca como **No Cumple**.

<div class="defense-box" markdown>

**Frase clave:**  
“El checklist refleja evidencia, no intención. Por eso se marca Cumple cuando hay sustento verificable y No Cumple cuando falta formalidad o evidencia suficiente.”

</div>
