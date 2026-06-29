# Tienda

El módulo Tienda permite administrar productos, categorías, carrito, pedidos y checkout dentro de un sitio.

## Prefijo

```text
/api/v1/sitios/{sitio_id}/tienda
```

## Productos

| Método | Ruta | Función |
|---|---|---|
| GET | `/productos` | Listar productos públicos. |
| GET | `/admin/productos` | Listar productos para administración. |
| POST | `/productos` | Crear producto. |
| GET | `/productos/{producto_id}` | Obtener producto público. |
| GET | `/admin/productos/{producto_id}` | Obtener producto administrativo. |
| PUT | `/productos/{producto_id}` | Actualizar producto. |
| DELETE | `/productos/{producto_id}` | Eliminar producto. |

## Categorías

| Método | Ruta | Función |
|---|---|---|
| GET | `/categorias` | Listar categorías públicas. |
| GET | `/admin/categorias` | Listar categorías administrativas. |
| POST | `/categorias` | Crear categoría. |
| GET | `/categorias/{categoria_id}` | Obtener categoría pública. |
| GET | `/admin/categorias/{categoria_id}` | Obtener categoría administrativa. |
| PUT | `/categorias/{categoria_id}` | Actualizar categoría. |
| DELETE | `/categorias/{categoria_id}` | Eliminar categoría. |

## Pedidos

| Método | Ruta | Función |
|---|---|---|
| GET | `/pedidos` | Listar pedidos. |
| GET | `/pedidos/{pedido_id}` | Obtener pedido. |
| PUT | `/pedidos/{pedido_id}/estado` | Actualizar estado de pedido. |

## Carrito y checkout

| Método | Ruta | Función |
|---|---|---|
| GET | `/carrito` | Obtener carrito. |
| POST | `/carrito/items` | Agregar ítem al carrito. |
| PUT | `/carrito/items/{item_id}` | Actualizar cantidad. |
| DELETE | `/carrito/items/{item_id}` | Eliminar ítem del carrito. |
| POST | `/checkout` | Realizar checkout. |

## Validaciones esperadas

- El módulo Tienda debe estar activo para el sitio.
- Los productos y pedidos deben pertenecer al `sitio_id` correcto.
- Las operaciones administrativas deben exigir permisos.
- El checkout debe validar productos, cantidades y estado del carrito.
