# Sitios, plantillas y módulos

Estos endpoints forman parte del core de All-InOne, ya que permiten administrar tenants, diseños reutilizables y módulos activables.

## Sitios

Prefijo:

```text
/api/sitios
```

| Método | Ruta | Función |
|---|---|---|
| POST | `/api/sitios/` | Crear sitio. |
| GET | `/api/sitios/` | Listar sitios. |
| GET | `/api/sitios/mis-sitios` | Listar sitios asociados al usuario. |
| GET | `/api/sitios/{sitio_id}` | Obtener detalle de un sitio. |
| PUT | `/api/sitios/{sitio_id}` | Actualizar sitio. |
| DELETE | `/api/sitios/{sitio_id}` | Eliminar o desactivar sitio. |

## Plantillas

Prefijo:

```text
/api/plantillas
```

| Método | Ruta | Función |
|---|---|---|
| GET | `/api/plantillas/publicas` | Lista plantillas públicas. |
| GET | `/api/plantillas/mis-plantillas` | Lista plantillas del usuario o sitio. |
| GET | `/api/plantillas` | Lista todas las plantillas. |
| GET | `/api/plantillas/{plantilla_id}` | Obtiene una plantilla. |
| POST | `/api/plantillas` | Crea plantilla. |
| PUT | `/api/plantillas/{plantilla_id}` | Actualiza plantilla. |
| DELETE | `/api/plantillas/{plantilla_id}` | Elimina plantilla. |

## Módulos

Prefijo:

```text
/api/modulos
```

| Método | Ruta | Función |
|---|---|---|
| POST | `/api/modulos/` | Crear módulo. |
| GET | `/api/modulos/` | Listar módulos. |
| GET | `/api/modulos/{modulo_id}` | Obtener módulo. |
| PUT | `/api/modulos/{modulo_id}` | Actualizar módulo. |
| DELETE | `/api/modulos/{modulo_id}` | Eliminar módulo. |

## Activación de módulos por sitio

Prefijo:

```text
/api/sitios/{sitio_id}/modulos
```

| Método | Ruta | Función |
|---|---|---|
| GET | `/api/sitios/{sitio_id}/modulos/` | Lista módulos del sitio. |
| POST | `/api/sitios/{sitio_id}/modulos/{modulo_id}` | Activa un módulo en el sitio. |
| DELETE | `/api/sitios/{sitio_id}/modulos/{modulo_id}` | Desactiva un módulo del sitio. |

## Validaciones esperadas

- El usuario debe tener permisos suficientes.
- El módulo debe existir.
- El sitio debe existir.
- La activación debe asociarse al sitio correcto.
- No debe permitirse manipular módulos de sitios ajenos.
