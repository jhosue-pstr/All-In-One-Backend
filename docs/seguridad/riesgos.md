# Riesgos y consideraciones de seguridad

Esta sección resume riesgos relevantes para el backend de All-InOne.

## Riesgos principales

| Riesgo | Impacto | Medida recomendada |
|---|---|---|
| Acceso cruzado entre tenants | Alto | Validar siempre `site_id` o `sitio_id` en consultas y operaciones. |
| Token JWT mal gestionado | Alto | Controlar expiración, firma y validación del token. |
| Permisos insuficientemente verificados | Alto | Centralizar validaciones RBAC. |
| Entradas no validadas | Medio/Alto | Usar esquemas Pydantic y validaciones de negocio. |
| Eliminación física de datos críticos | Medio | Aplicar soft delete donde corresponda. |
| Falta de trazabilidad | Medio | Registrar operaciones críticas mediante auditoría. |
| Endpoints públicos excesivamente abiertos | Medio/Alto | Revisar exposición de información y controles por sitio. |

## Recomendaciones generales

- Revisar endpoints críticos con pruebas automatizadas.
- Validar permisos para cada rol.
- Probar separación de datos entre sitios.
- Mantener evidencias de pruebas de seguridad.
- Documentar vulnerabilidades encontradas y su tratamiento.
