# Resumen de endpoints

El backend expone endpoints REST agrupados por dominio. FastAPI genera documentación interactiva mediante Swagger/OpenAPI, lo cual permite probar la API, revisar modelos de entrada/salida y validar seguridad mediante tokens.

## Grupos principales

| Grupo | Prefijo aproximado | Propósito |
|---|---|---|
| Autenticación interna | `/api/auth` | Registro, login, perfil y actualización de usuario interno. |
| Sitios | `/api/sitios` | Gestión de tenants o sitios del sistema. |
| Plantillas | `/api/plantillas` | Gestión de diseños reutilizables. |
| Módulos | `/api/modulos` | Catálogo de funcionalidades activables. |
| Sitio-Módulo | `/api/sitios/{id}/modulos` | Activación o desactivación de módulos por sitio. |
| Roles y permisos | `/api/roles` | Gestión de permisos, usuarios administrativos y roles. |
| Render público | `/{slug}` | Renderizado o consulta pública de sitios. |
| Auth Público | Rutas por sitio | Registro/login de usuarios externos. |
| Blog | `/api/modules/blog` | Categorías, posts y carga de imágenes. |
| Tienda | `/api/v1/sitios/{sitio_id}/tienda` | Productos, categorías, carrito, pedidos y checkout. |
| Analítica | `/api/modules/analitica` | Visitas, eventos y dashboard. |

!!! note "Prefijos"
    Algunos routers tienen prefijos definidos directamente y otros se integran con prefijo general `/api` desde `app/main.py`. Para confirmar la ruta exacta, la fuente más segura es Swagger en `/docs`.

## Endpoints de salud y archivos públicos

Además de la API funcional, el backend expone:

| Recurso | Uso |
|---|---|
| `/` | Respuesta básica de verificación. |
| `/health` | Verificación de conexión con base de datos. |
| `/media` | Archivos asociados a plantillas y sitios. |
| `/uploads` | Archivos cargados desde módulos como Blog o Tienda. |
| `/static` | Recursos estáticos, como el widget público. |

## Lectura por tipo de endpoint

| Tipo | Característica |
|---|---|
| Público | No requiere token administrativo; orientado a visitantes o sitios publicados. |
| Administrativo | Requiere JWT y permisos según rol. |
| Modular | Pertenece a Blog, Tienda, Analítica o Auth Público. |
| Técnico | Salud, documentación y archivos estáticos. |

## Valor para auditoría

Los endpoints permiten contrastar lo documentado con lo implementado. Si un módulo está descrito en el informe, la auditoría puede buscar evidencia en:

- router registrado en `main.py`;
- endpoint visible en Swagger;
- modelo de datos asociado;
- servicio o lógica de negocio;
- pruebas automatizadas;
- evidencia de seguridad o permisos.

<div class="defense-box" markdown>
**Frase para exposición:** “Swagger/OpenAPI permite validar la existencia real de endpoints y sirve como evidencia técnica para contrastar documentación e implementación.”
</div>
