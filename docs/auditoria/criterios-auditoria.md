# Criterios de auditoría

Los criterios de auditoría son las referencias usadas para evaluar el proyecto. Permiten que la revisión no dependa de opiniones personales, sino de estándares, buenas prácticas y evidencias verificables.

## Criterios utilizados

| Criterio | Uso dentro de la auditoría |
|---|---|
| ISO/IEC 12207 | Evaluar procesos del ciclo de vida del software: desarrollo, documentación, verificación, validación y mantenimiento. |
| ISO/IEC 25010 | Evaluar calidad del producto: funcionalidad, rendimiento, usabilidad, seguridad, mantenibilidad, portabilidad y fiabilidad. |
| CMMI-DEV | Evaluar madurez de procesos: requisitos, planificación, seguimiento, calidad, verificación y validación. |
| Checklist SDLC | Instrumento operativo para revisar metodología, necesidades, diseño, pruebas, implementación, mantenimiento y documentación. |
| Buenas prácticas de desarrollo seguro | Revisar autenticación, autorización, validación de entradas, errores, roles, permisos y aislamiento multitenant. |
| Buenas prácticas DevSecOps | Revisar GitHub, Jenkins, SonarCloud/SonarQube, Snyk, Playwright, k6 y Swagger/OpenAPI. |
| Documentación formal del proyecto | Contrastar informe principal, Jira, pruebas, seguridad, calidad, backend, frontend y evidencias. |

## Cómo se usan los criterios

La auditoría aplica los criterios comparando tres elementos:

```text
Criterio esperado  →  Evidencia disponible  →  Conclusión de auditoría
```

Por ejemplo:

| Caso | Criterio | Evidencia | Resultado posible |
|---|---|---|---|
| Pruebas | Deben existir procedimientos y resultados documentados. | Reportes funcionales, E2E, k6, ZAP, Sonar/Snyk. | Cumple si la evidencia es suficiente. |
| Implementación | Debe existir pase formal a producción o procedimiento oficial. | Jenkins/despliegue de prueba, pero no producción real. | No cumple si no hay implementación formal. |
| Documentación | Debe permitir trazabilidad del ciclo de vida. | Informe, Jira, MkDocs, reportes y código. | Cumple si permite relacionar requisitos, módulos y pruebas. |

!!! warning "Diferencia importante"
    Un entorno de prueba o académico no equivale a una implementación productiva formal. Por eso algunos ítems técnicos pueden existir, pero aun así marcarse como **No Cumple** cuando el checklist exige formalidad empresarial.

## Frase clave

<div class="defense-box" markdown>

**“Los criterios de auditoría permiten evaluar el proyecto con base objetiva: estándares, checklist, documentación y evidencias técnicas.”**

</div>
