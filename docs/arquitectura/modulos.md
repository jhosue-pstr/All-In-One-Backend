# Módulos del sistema

El backend organiza varias funcionalidades como módulos dentro del monolito modular.

## Módulos implementados o documentados

| Módulo | Ubicación principal | Propósito |
|---|---|---|
| Core | `app/api/`, `app/service/`, `app/models/` | Autenticación interna, usuarios, roles, permisos, sitios y plantillas. |
| Blog | `app/packages/modulos/blog/` | Gestión de categorías, publicaciones, imágenes y estados de publicación. |
| Tienda | `app/packages/modulos/store/` | Gestión de productos, categorías, carrito, pedidos y checkout. |
| Auth Público | `app/api/site_auth.py` y `app/packages/modulos/SiteAuth/` | Registro e inicio de sesión de usuarios finales por sitio. |
| Analítica | `app/packages/modulos/analitica/` | Registro de visitas, eventos y métricas por sitio. |
| Inventario | `app/packages/modulos/inventory/` | Módulo reservado o planificado; debe validarse según evidencia real. |

## Activación de módulos por sitio

El sistema permite asociar módulos a un sitio mediante endpoints de sitio-módulo. Esto permite que un tenant tenga activo Blog, Tienda u otras capacidades según necesidad.

## Estado de módulos

Para auditoría se recomienda clasificar cada módulo como:

| Estado | Criterio |
|---|---|
| Implementado | Tiene rutas, modelos, servicios, esquemas y evidencia funcional. |
| Parcial | Tiene parte de la estructura, pero faltan componentes o pruebas. |
| Planificado | Está documentado o creado como carpeta, pero sin implementación funcional suficiente. |
| Futuro | Forma parte de la visión del producto, pero no debe evaluarse como terminado. |

!!! important "Cuidado con Inventario"
    Si un módulo solo tiene una carpeta o archivo inicial, no debe presentarse como completamente implementado.
