# Autenticación interna

La autenticación interna corresponde al acceso de usuarios administrativos al panel de All-InOne.

## Prefijo

```text
/api/auth
```

## Endpoints

| Método | Ruta | Función |
|---|---|---|
| POST | `/api/auth/registro` | Registra un usuario interno. |
| POST | `/api/auth/inicio` | Inicia sesión y genera token. |
| GET | `/api/auth/me` | Obtiene información del usuario autenticado. |
| PUT | `/api/auth/me` | Actualiza información del usuario autenticado. |

## Flujo general

```text
Usuario envía credenciales
      ↓
Backend valida credenciales
      ↓
Se genera token JWT
      ↓
Frontend almacena token
      ↓
Solicitudes posteriores usan Authorization: Bearer TOKEN
```

## Aspectos de seguridad

- Validar credenciales.
- Proteger rutas privadas.
- Asociar usuario con rol.
- Aplicar permisos según rol.
- Evitar exposición innecesaria de datos sensibles.
