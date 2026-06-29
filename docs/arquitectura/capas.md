# Capas y responsabilidades

El backend separa responsabilidades en capas lógicas. Esta separación facilita la mantenibilidad y permite auditar mejor la relación entre rutas, lógica de negocio, modelos y esquemas.

## Capas principales

| Capa | Ubicación | Responsabilidad |
|---|---|---|
| Entrada API | `app/api/` y `app/packages/modulos/*/routes.py` | Recibir solicitudes HTTP y exponer endpoints. |
| Servicios | `app/service/` y `app/packages/modulos/*/services.py` | Aplicar reglas de negocio. |
| Modelos | `app/models/` y `app/packages/modulos/*/models.py` | Representar entidades persistentes. |
| Esquemas | `app/schemas/` y `app/packages/modulos/*/schemas.py` | Validar entradas y respuestas. |
| Base de datos | `app/db/` | Configurar conexión, sesiones y datos semilla. |
| Core | `app/core/` | Configuración, permisos, middleware y utilidades transversales. |

## Ejemplo de flujo

```text
POST /api/sitios/
      ↓
Router de sitios
      ↓
Servicio de sitio
      ↓
Modelo Sitio
      ↓
Base de datos
```

## Criterio de revisión

Para validar un módulo, se debe revisar si cuenta con:

- Ruta o endpoint.
- Servicio o lógica de negocio.
- Modelo de datos.
- Esquema de entrada/salida.
- Pruebas o evidencia funcional.
- Control de permisos cuando corresponda.
