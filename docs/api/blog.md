# API del módulo Blog

El módulo Blog permite que un sitio gestione contenido informativo mediante categorías y publicaciones. Este módulo es importante para PYMES que necesitan comunicar noticias, servicios, novedades o artículos desde su sitio web.

## Funcionalidades principales

| Recurso | Operaciones |
|---|---|
| Categorías | Crear, listar, actualizar y eliminar lógicamente categorías. |
| Posts | Crear, listar, consultar por slug, actualizar y eliminar lógicamente publicaciones. |
| Imágenes | Cargar imágenes asociadas al contenido. |
| Estados | Gestionar borradores, publicados, programados o archivados. |

## Rutas conceptuales

| Método | Ruta conceptual | Uso |
|---|---|---|
| POST | `/api/modules/blog/{site_id}/categories` | Crear categoría. |
| GET | `/api/modules/blog/{site_id}/categories` | Listar categorías del sitio. |
| PUT | `/api/modules/blog/{site_id}/categories/{category_id}` | Actualizar categoría. |
| DELETE | `/api/modules/blog/{site_id}/categories/{category_id}` | Eliminar categoría lógicamente. |
| POST | `/api/modules/blog/{site_id}/posts` | Crear publicación. |
| GET | `/api/modules/blog/{site_id}/posts` | Listar publicaciones públicas. |
| GET | `/api/modules/blog/{site_id}/admin/posts` | Listar publicaciones administrativas. |
| GET | `/api/modules/blog/{site_id}/posts/{slug}` | Consultar publicación pública por slug. |
| PUT | `/api/modules/blog/{site_id}/posts/{post_id}` | Actualizar publicación. |
| DELETE | `/api/modules/blog/{site_id}/posts/{post_id}` | Eliminar publicación lógicamente. |

## Vista pública vs administrativa

El módulo diferencia entre contenido público y contenido administrativo. La vista pública debe mostrar solo contenido disponible, mientras que la vista administrativa puede trabajar con borradores, programados, archivados o registros internos.

| Vista | Debe permitir |
|---|---|
| Pública | Ver posts publicados y disponibles. |
| Administrativa | Gestionar posts en distintos estados. |

## Seguridad y permisos

Las operaciones administrativas del Blog deben requerir permisos como ver, crear, editar o eliminar contenido. Esto evita que cualquier usuario modifique publicaciones del sitio.

## Soft delete

El módulo Blog incluye eliminación lógica para categorías y publicaciones. Esto permite ocultar contenido sin perder completamente el historial.

<div class="defense-box" markdown>
**Frase para exposición:** “El módulo Blog evidencia separación entre uso público y administración interna, además de aplicar permisos y eliminación lógica para proteger el contenido.”
</div>
