# Multitenancy

All-InOne está orientado a pequeñas y medianas empresas que pueden gestionar su propio sitio dentro de la plataforma. Por ello, el backend aplica un enfoque multitenant basado en sitios.

## Qué significa multitenancy

En este proyecto, un **tenant** representa un sitio o negocio dentro de la plataforma. Cada sitio debe mantener su información separada de los demás.

```text
Plataforma All-InOne
├─ Sitio A / Tenant A
│  ├─ Blog
│  ├─ Tienda
│  └─ Usuarios públicos
├─ Sitio B / Tenant B
│  ├─ Blog
│  ├─ Tienda
│  └─ Usuarios públicos
└─ Sitio C / Tenant C
```

## Objetivo del aislamiento

El aislamiento multitenant busca evitar que:

- Un usuario vea información de otro sitio.
- Un administrador modifique módulos de un sitio ajeno.
- Los productos, posts, pedidos o métricas se mezclen entre tenants.
- Los usuarios públicos de un sitio accedan a recursos de otro.

## Evidencias técnicas esperadas

Para validar multitenancy se deben revisar:

- Uso de identificadores como `sitio_id` o `site_id`.
- Filtros por sitio en consultas.
- Endpoints que reciben el identificador del sitio.
- Asociación de módulos, contenido y usuarios públicos a un sitio.
- Pruebas que validen separación de información.

## Componentes relacionados

| Componente | Relación con multitenancy |
|---|---|
| Sitios | Entidad central del tenant. |
| Blog | Publicaciones asociadas a un sitio. |
| Tienda | Productos, categorías y pedidos asociados a un sitio. |
| Auth Público | Usuarios finales asociados al sitio. |
| Analítica | Métricas registradas por sitio. |

!!! warning "Riesgo principal"
    El riesgo más importante del multitenancy es el acceso cruzado entre tenants. Por eso debe verificarse en endpoints, servicios y pruebas.
