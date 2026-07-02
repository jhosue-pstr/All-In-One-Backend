# Riesgos de auditoría

La matriz de riesgos identifica situaciones que podrían afectar la calidad o ejecución de la auditoría.

## Riesgos más importantes

| Riesgo | Por qué importa |
|---|---|
| Documentación incompleta | Puede limitar conclusiones. |
| Diferencias entre documentación y código | Puede generar hallazgos críticos. |
| Pruebas incompletas o desactualizadas | Afecta validación del sistema. |
| Acceso limitado al entorno funcional | Obliga a trabajar con evidencias alternativas. |
| Complejidad multitenant | Requiere revisión cuidadosa de seguridad y datos. |
| Módulos parciales o futuros | Evita asumir como implementado lo que aún no está completo. |
| Evidencias de distintas fechas | Puede generar inconsistencias de versión. |

## Estrategia general

La respuesta principal es contrastar documentación, Jira, código, pruebas, reportes y evidencias técnicas.

!!! warning "Riesgo crítico"
    Uno de los riesgos más fuertes es que lo documentado no coincida completamente con lo implementado.
