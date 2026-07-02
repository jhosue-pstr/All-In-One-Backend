# Defensa en exposición

Esta página resume preguntas probables y respuestas cortas para defender la auditoría y el checklist.

## Preguntas sobre Project Charter

??? question "¿Para qué sirve el Project Charter?"
    Sirve para formalizar la auditoría: define objetivo, alcance, exclusiones, criterios, metodología, entregables, cronograma, riesgos, supuestos, restricciones y cierre.

??? question "¿Por qué auditar All-InOne?"
    Porque es una plataforma SaaS multitenant con módulos, roles, permisos, constructor visual, pruebas, seguridad y documentación. Esa complejidad exige verificar coherencia entre lo planificado, documentado, implementado y probado.

??? question "¿La auditoría certifica el sistema?"
    No. Es una auditoría académica y técnica. Evalúa evidencias y propone mejoras, pero no constituye certificación oficial ni garantía productiva.

## Preguntas sobre checklist

??? question "¿Por qué no todo está marcado como Cumple?"
    Porque el checklist se basa en evidencia. Cuando no existe evidencia formal suficiente, o cuando el proyecto no llega a producción real, corresponde marcar No Cumple.

??? question "¿Por qué CL-05 Implementación está como No Cumple si hay Jenkins o despliegue de prueba?"
    Porque Jenkins o un despliegue técnico de prueba no equivalen a un procedimiento formal de promoción a producción en una empresa real.

??? question "¿Por qué CL-06 Post-implementación está como No Cumple?"
    Porque no hubo implementación formal en producción; por tanto, no puede existir una revisión post-implementación real.

??? question "¿Por qué MkDocs no convierte todo en Cumple?"
    Porque MkDocs mejora la documentación, pero no reemplaza autorizaciones formales, gestión de cambios productivos, revisión post-implementación o herramientas CASE.

??? question "¿Por qué CL-01-03 está como No Cumple si se usa Jira?"
    Jira ayuda a gestionar tareas y sprints, pero el ítem pregunta por herramientas CASE formales, orientadas al modelado o generación de artefactos. No se evidencia uso formal de CASE.

??? question "¿Cuál es el riesgo más crítico?"
    R-02: diferencias entre documentación e implementación real, porque puede afectar directamente la validez de las conclusiones.

## Respuestas rápidas para recordar

| Tema | Respuesta corta |
|---|---|
| Project Charter | Documento que formaliza y delimita la auditoría. |
| Checklist | Instrumento para evaluar cumplimiento con evidencia. |
| MkDocs | Documentación navegable del sistema y auditoría. |
| Implementación | Prueba técnica no es producción formal. |
| Post-implementación | Solo aplica después de una implementación real. |
| Riesgos | Anticipan problemas que pueden afectar la auditoría. |
| Factores críticos | Condiciones necesarias para que la auditoría sea exitosa. |

<div class="defense-box" markdown>

**Frase final para exposición:**  
“El objetivo no fue marcar todo como cumple, sino evaluar con honestidad el estado del proyecto según evidencias, criterios técnicos y el contexto académico de All-InOne.”

</div>
