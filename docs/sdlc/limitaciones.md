# Limitaciones técnicas y de alcance

Aunque el backend cuenta con evidencias técnicas sólidas, la documentación debe reconocer sus límites. Esto evita afirmar más de lo que realmente se puede demostrar.

## Limitaciones principales

| Limitación | Interpretación correcta |
|---|---|
| Contexto académico | El sistema se desarrolló para un curso y no como operación empresarial formal. |
| Despliegue de prueba | Existen evidencias técnicas, pero no producción formal. |
| Revisión no exhaustiva | La auditoría no revisa línea por línea todo el código. |
| Módulos en evolución | Algunos elementos pueden estar implementados, parciales o planificados. |
| Seguridad no ofensiva | ZAP y revisión técnica no equivalen a pentesting profundo. |
| Code review formal | GitHub y análisis estático no sustituyen un flujo formal documentado de revisores. |

## Cómo defenderlo

No se debe presentar estas limitaciones como fallas absolutas. Son condiciones reales del alcance del proyecto. Una auditoría seria reconoce qué evidencia tiene y qué no puede concluir.

## Diferencia clave

| Evidencia existente | Lo que no debe asumirse |
|---|---|
| Jenkins / CI de prueba | Despliegue productivo formal. |
| Pruebas automatizadas | Cobertura total de todos los escenarios. |
| Swagger | Manual completo de operación para usuario final. |
| MkDocs | Certificación oficial del sistema. |
| ZAP | Pentesting profesional completo. |

## Relación con el Project Charter

Estas limitaciones son coherentes con el alcance y exclusiones de la auditoría SDLC. La documentación técnica debe mantener esa misma postura: mostrar fortalezas, pero también declarar límites de forma honesta.

<div class="defense-box" markdown>
**Frase para exposición:** “La documentación del backend diferencia claramente evidencia técnica de prueba y cumplimiento formal productivo; por eso las conclusiones son más defendibles.”
</div>
