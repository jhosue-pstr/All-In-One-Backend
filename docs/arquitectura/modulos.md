# Módulos del sistema

El backend organiza funcionalidades en módulos que representan capacidades del sistema.

## Módulos principales

| Módulo | Función |
|---|---|
| Sitios | Administración de tenants o sitios. |
| Plantillas | Diseños reutilizables para páginas. |
| Blog | Publicaciones, categorías e imágenes. |
| Tienda | Productos, categorías, pedidos y checkout. |
| Auth Público | Registro e inicio de sesión de usuarios externos. |
| Analítica | Eventos, visitas, sesiones y métricas. |
| Auditoría | Registro de acciones relevantes. |
| Soft delete | Eliminación lógica de registros. |

## Consideración de auditoría

No todos los módulos deben asumirse como completamente implementados sin evidencia. La auditoría debe contrastar cada módulo contra:

- Código fuente.
- Rutas.
- Servicios.
- Modelos.
- Componentes frontend relacionados.
- Pruebas.
- Documentación.
