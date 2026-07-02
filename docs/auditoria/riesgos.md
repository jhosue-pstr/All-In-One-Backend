# Riesgos de auditoría

La matriz de riesgos identifica condiciones que podrían afectar la calidad, suficiencia o confiabilidad de la auditoría.

## Resumen visual

<div class="kpi-grid" markdown>

<div class="kpi-card" markdown>
<strong>1</strong>
Riesgo crítico
</div>

<div class="kpi-card" markdown>
<strong>7</strong>
Riesgos altos
</div>

<div class="kpi-card" markdown>
<strong>5</strong>
Riesgos medios
</div>

<div class="kpi-card" markdown>
<strong>13</strong>
Riesgos totales
</div>

</div>

## Matriz resumida de riesgos

| ID | Riesgo | Nivel | Respuesta principal |
|---|---|---|---|
| R-01 | Documentación incompleta o dispersa. | Alto | Solicitar documentación y registrar ausencias. |
| R-02 | Diferencias entre documentación e implementación real. | Crítico | Contrastar documentos con código, rutas, servicios y componentes. |
| R-03 | Evidencias de pruebas incompletas o desactualizadas. | Alto | Revisar reportes y brechas de cobertura. |
| R-04 | Acceso limitado a entorno funcional estable. | Medio | Usar evidencias equivalentes: capturas, videos, reportes y código. |
| R-05 | Complejidad técnica SaaS multitenant y monolito modular. | Alto | Dividir revisión por dominios funcionales. |
| R-06 | Falta de disponibilidad del equipo auditado. | Medio | Coordinar consultas y usar evidencias documentales. |
| R-07 | Cambios de alcance durante la auditoría. | Medio | Mantener alcance aprobado y registrar cambios. |
| R-08 | Recursos limitados del equipo auditor. | Alto | Priorizar componentes críticos. |
| R-09 | Sesgo académico. | Medio | Aplicar criterios objetivos y evidencia verificable. |
| R-10 | Desorden o duplicidad de papeles de trabajo. | Medio | Centralizar evidencias con control de versiones. |
| R-11 | Interpretar módulos parciales como implementados. | Alto | Validar cada módulo contra evidencia real. |
| R-12 | Riesgos de seguridad no detectados documentalmente. | Alto | Revisar ZAP, JWT, roles, permisos y rutas protegidas. |
| R-13 | Evidencias de diferentes fechas o versiones. | Medio | Revisar fuente, fecha y versión antes de usar evidencia. |

## Riesgos más importantes para defender

### R-02: Diferencias entre documentación y código

Este es crítico porque puede afectar directamente la conclusión de auditoría. Si un módulo aparece documentado, pero no existe en el backend o frontend, se debe registrar como brecha documental o técnica.

### R-11: Módulos parciales o planificados

Es importante diferenciar entre módulo implementado, parcial, planificado o futuro. La auditoría no debe asumir que una funcionalidad está completa solo porque aparece en la documentación.

### R-04: Entorno funcional limitado

Como el proyecto es académico, puede no existir una implementación productiva permanente. En ese caso, se pueden usar evidencias equivalentes: capturas, reportes, Swagger, Jenkins, videos, pruebas y código fuente.

## Escalas usadas

| Escala | Descripción |
|---|---|
| Probabilidad baja | Menor al 30%. |
| Probabilidad media | Entre 30% y 60%. |
| Probabilidad alta | Mayor al 60%. |
| Impacto bajo | Afecta de forma menor. |
| Impacto medio | Puede retrasar o limitar conclusiones. |
| Impacto alto | Compromete la calidad del análisis o la evidencia. |

<div class="defense-box" markdown>

**Frase para exposición:**  
“La matriz de riesgos permite anticipar problemas que podrían afectar la auditoría y definir una respuesta antes de que comprometan la evidencia o las conclusiones.”

</div>
