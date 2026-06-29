# Blog

El módulo Blog permite gestionar categorías y publicaciones por sitio.

## Prefijo

```text
/api/modules/blog
```

## Categorías

| Método | Ruta | Función |
|---|---|---|
| POST | `/api/modules/blog/{site_id}/categories` | Crear categoría. |
| GET | `/api/modules/blog/{site_id}/categories` | Listar categorías. |
| PUT | `/api/modules/blog/{site_id}/categories/{category_id}` | Actualizar categoría. |
| DELETE | `/api/modules/blog/{site_id}/categories/{category_id}` | Eliminar categoría. |

## Publicaciones

| Método | Ruta | Función |
|---|---|---|
| POST | `/api/modules/blog/{site_id}/posts` | Crear publicación. |
| GET | `/api/modules/blog/{site_id}/posts` | Listar publicaciones públicas. |
| GET | `/api/modules/blog/{site_id}/admin/posts` | Listar publicaciones administrativas. |
| GET | `/api/modules/blog/{site_id}/posts/{slug}` | Obtener publicación por slug. |
| PUT | `/api/modules/blog/{site_id}/posts/{post_id}` | Actualizar publicación. |
| DELETE | `/api/modules/blog/{site_id}/posts/{post_id}` | Eliminar publicación. |

## Validaciones esperadas

- El módulo Blog debe estar activo en el sitio.
- Las publicaciones deben asociarse al `site_id` correcto.
- El contenido público debe respetar el estado de publicación.
- Las operaciones administrativas deben requerir permisos.
