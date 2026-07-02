# Trazabilidad de evidencias

La trazabilidad permite conectar lo que el proyecto dice, lo que se planificó, lo que se implementó y lo que se probó.

## Cadena de trazabilidad

```text
Requisito → Historia de usuario → Sprint / tarea Jira → Módulo → Código → Prueba → Evidencia → Conclusión de auditoría
```

## Fuentes de evidencia

| Fuente | Qué evidencia aporta |
|---|---|
| Project Charter | Objetivos, alcance, criterios, metodología, riesgos y cierre de auditoría. |
| Checklist SDLC | Evaluación operativa de cumplimiento / no cumplimiento. |
| Informe principal | Descripción del sistema, arquitectura, módulos y decisiones técnicas. |
| Jira | Sprints, tareas, subtareas, responsables, fechas y criterios de aceptación. |
| Backend | Rutas, servicios, modelos, esquemas, autenticación, permisos, auditoría y soft delete. |
| Frontend | Rutas, componentes, páginas, consumo de API, WebEditor y protección visual. |
| Swagger/OpenAPI | Documentación de endpoints y contratos técnicos. |
| Playwright / E2E | Validación de flujos críticos desde la interfaz. |
| k6 | Evidencia de rendimiento. |
| OWASP ZAP / Snyk | Evidencia de seguridad y vulnerabilidades. |
| SonarCloud/SonarQube | Calidad, duplicación, mantenibilidad, bugs y vulnerabilidades. |
| Jenkins | Integración continua y ejecución técnica de pipeline de prueba. |
| MkDocs | Documentación navegable y ordenada del sistema y auditoría. |

## Ejemplo de trazabilidad

| Elemento | Ejemplo |
|---|---|
| Requisito | Gestión de sitios por tenant. |
| Historia / tarea | Crear, editar y listar sitios en Jira. |
| Backend | Endpoints, servicios y modelos relacionados con sitios. |
| Frontend | Pantallas y formularios de administración de sitios. |
| Prueba | Prueba funcional o E2E del flujo de sitios. |
| Evidencia | Captura, reporte Playwright, Swagger, código o resultado de ejecución. |
| Conclusión | Cumple si se observa coherencia suficiente entre todos los elementos. |

## Por qué importa

Sin trazabilidad, una auditoría puede quedar como opinión. Con trazabilidad, cada conclusión se puede justificar con evidencia.

<div class="defense-box" markdown>

**Frase para exposición:**  
“La trazabilidad permite demostrar que cada conclusión del checklist se sustenta en evidencias y no solo en una afirmación del equipo.”

</div>
