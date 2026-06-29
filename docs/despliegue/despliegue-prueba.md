# Despliegue de prueba

El backend cuenta con evidencias y archivos relacionados con ejecución técnica, contenedores, Jenkins y herramientas de validación.

!!! warning "Importante"
    Este despliegue corresponde a un entorno académico/de prueba. No representa implementación oficial en una empresa ni puesta en producción formal.

## Archivos relacionados

| Archivo | Uso |
|---|---|
| `Dockerfile` | Construcción de imagen del backend. |
| `Jenkinsfile` | Flujo de integración continua. |
| `docker-compose.k6.yml` | Ejecución de pruebas de rendimiento. |
| `docker-compose.zap.yml` | Ejecución de pruebas de seguridad. |
| `Dockerfile.k6-tests` | Contenedor asociado a pruebas k6. |
| `Dockerfile.grafana` | Configuración relacionada con visualización de métricas. |

## Diferencia entre prueba y producción

| Aspecto | Despliegue de prueba | Producción formal |
|---|---|---|
| Objetivo | Validar funcionamiento técnico. | Operar para usuarios reales. |
| Aprobación | Académica o técnica. | Formal, con responsables y autorización. |
| Usuarios | Equipo de desarrollo/evaluación. | Empresa o clientes reales. |
| Cambios | Flexibles. | Controlados por gestión de cambios. |
| Evidencia | Capturas, logs, pruebas, reportes. | Actas, aprobaciones, monitoreo y soporte. |

## Evidencia útil para auditoría

- URL o entorno de prueba.
- Capturas de ejecución.
- Logs de Jenkins.
- Reportes de k6.
- Reportes de OWASP ZAP.
- Swagger/OpenAPI funcionando.
- Resultado de health check.
