# Metodología de auditoría

La auditoría se organiza en cuatro fases. Cada fase tiene actividades y entregables que permiten avanzar desde la planificación hasta el cierre.

<div class="timeline" markdown>

<div class="item" markdown>
### Fase 1: Preparar y planificar
Se definen criterios, objetivos, alcance, exclusiones, roles, estándares, modelo SDLC, stack tecnológico, evidencias requeridas y checklist adaptado.

**Entregables:** Plan de Auditoría, Checklist SDLC, comunicación de inicio y matriz inicial de evidencias.
</div>

<div class="item" markdown>
### Fase 2: Describir el proceso de desarrollo
Se revisa el informe del proyecto, Jira, backend, frontend, arquitectura, módulos, roles, permisos, Swagger, pruebas, reportes de calidad y evidencias DevSecOps.

**Entregables:** Registro de evidencias, papeles de trabajo, descripción del proceso SDLC y matriz preliminar de observaciones.
</div>

<div class="item" markdown>
### Fase 3: Evaluar y reportar
Se compara la evidencia contra ISO/IEC 12207, ISO/IEC 25010, CMMI-DEV y checklist SDLC. Se identifican conformidades, no conformidades, brechas, riesgos y recomendaciones.

**Entregables:** Matriz de hallazgos, matriz de riesgos, informe preliminar, informe final y recomendaciones.
</div>

<div class="item" markdown>
### Fase 4: Seguimiento
Se presenta el informe final, se solicita el plan de acción correctiva, se asignan responsables, se revisa el avance y se elabora el acta de cierre.

**Entregables:** Plan de acción correctiva, registro de seguimiento, evidencias de atención y acta de cierre.
</div>

</div>

## Enfoque general

La auditoría tiene un enfoque:

| Enfoque | Significado |
|---|---|
| Documental | Revisa documentos, informes, Jira, reportes y evidencias. |
| Técnico | Contrasta arquitectura, backend, frontend, pruebas, seguridad y calidad. |
| Metodológico | Evalúa si el proceso siguió un ciclo de vida ordenado. |
| Evaluativo | Identifica hallazgos y recomendaciones, pero no corrige directamente el código. |

## Flujo de trabajo de la auditoría

```text
Planificar → Recolectar evidencia → Contrastar evidencia → Evaluar → Reportar → Hacer seguimiento
```

## Pregunta probable

??? question "¿Por qué la auditoría no modifica el código?"
    Porque el rol del auditor es evaluar de forma objetiva, identificar hallazgos y emitir recomendaciones. Las correcciones corresponden al equipo responsable del desarrollo.

<div class="defense-box" markdown>

**Frase clave:**  
“La metodología asegura que la auditoría tenga fases, evidencias, entregables y cierre formal; no es una revisión improvisada del sistema.”

</div>
