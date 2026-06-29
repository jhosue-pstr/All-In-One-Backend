# Auth público

El Auth Público permite que usuarios finales se registren e inicien sesión dentro de un sitio generado por All-InOne.

## Prefijo

```text
/api/site-auth
```

## Endpoints

| Método | Ruta | Función |
|---|---|---|
| POST | `/api/site-auth/registro` | Registra usuario público de un sitio. |
| POST | `/api/site-auth/login` | Inicia sesión de usuario público. |
| POST | `/api/site-auth/logout` | Cierra sesión. |
| GET | `/api/site-auth/me` | Obtiene datos del usuario público autenticado. |
| PUT | `/api/site-auth/me` | Actualiza datos del usuario público. |
| GET | `/api/site-auth/usuarios` | Lista usuarios públicos del sitio. |
| GET | `/api/site-auth/verify` | Verifica token de usuario público. |

## Diferencia con autenticación interna

| Tipo | Usuario | Uso |
|---|---|---|
| Auth interna | Administradores, editores, gestores | Panel administrativo. |
| Auth público | Usuarios finales del sitio | Interacción pública por tenant. |

## Riesgo a controlar

El usuario público de un sitio no debe acceder a datos de otro sitio. Por eso las consultas deben considerar el sitio asociado.
