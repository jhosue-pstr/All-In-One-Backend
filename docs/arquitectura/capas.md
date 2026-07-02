# Capas internas

El backend se entiende como una aplicación organizada por capas internas.

## Capas comunes

| Capa | Función |
|---|---|
| Rutas / routers | Reciben las solicitudes HTTP. |
| Servicios | Contienen lógica de negocio. |
| Modelos | Representan entidades persistentes. |
| Schemas | Validan entrada y salida de datos. |
| Base de datos | Almacena información relacional. |
| Seguridad | Gestiona autenticación, permisos y roles. |

## Ventajas

- Mejora la mantenibilidad.
- Reduce acoplamiento.
- Permite probar partes del sistema.
- Facilita ubicar errores.
- Ayuda a separar responsabilidades.

!!! note "Punto de control SDLC"
    En auditoría se revisa que la arquitectura declarada coincida con esta organización real del código.
