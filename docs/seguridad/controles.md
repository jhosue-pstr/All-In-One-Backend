# Controles principales de seguridad

El backend incorpora controles orientados a proteger una plataforma SaaS multitenant.

## Controles implementados o considerados

| Control | Descripción |
|---|---|
| JWT | Permite autenticar usuarios mediante tokens. |
| RBAC | Restringe acciones según roles y permisos. |
| Rutas protegidas | Evita acceso no autorizado a endpoints internos. |
| Multitenancy | Separa información por sitio o tenant. |
| Validación de entradas | Reduce errores y entradas inválidas. |
| Auditoría | Registra acciones relevantes. |
| Soft delete | Preserva información importante ante eliminaciones. |
| CORS | Controla orígenes permitidos para llamadas desde frontend. |

## Seguridad por capas

```text
Usuario
  ↓
Token JWT
  ↓
Validación de autenticación
  ↓
Validación de rol/permisos
  ↓
Validación de sitio/tenant
  ↓
Acceso al recurso
```

## Riesgos que se deben controlar

- Acceso sin autenticación.
- Escalada de privilegios.
- Acceso cruzado entre tenants.
- Manipulación de recursos de otro sitio.
- Eliminación física no controlada.
- Exposición de información sensible en respuestas.
