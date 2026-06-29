# Analítica

El módulo Analítica registra visitas, eventos y métricas asociadas a un sitio.

## Prefijo

```text
/api/modules/analitica
```

## Endpoints

| Método | Ruta | Función |
|---|---|---|
| POST | `/api/modules/analitica/{site_id}/visitas` | Registra una visita. |
| POST | `/api/modules/analitica/{site_id}/eventos` | Registra un evento. |
| GET | `/api/modules/analitica/{site_id}/dashboard` | Obtiene métricas del sitio. |

## Usos principales

- Medir visitas del sitio.
- Registrar eventos de navegación o interacción.
- Construir indicadores para el panel administrativo.

## Consideraciones

- Las métricas deben asociarse al sitio correcto.
- La información debe evitar cruces entre tenants.
- El dashboard debe mostrar datos filtrados por `site_id`.
