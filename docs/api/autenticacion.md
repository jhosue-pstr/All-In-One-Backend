# Autenticación

El backend utiliza autenticación basada en **JWT** para identificar usuarios y proteger rutas.

## Flujo general

1. El usuario inicia sesión.
2. El backend valida credenciales.
3. El sistema genera un token JWT.
4. El frontend usa el token para consumir endpoints protegidos.
5. El backend valida el token en cada solicitud crítica.

## Riesgos a revisar

- Tokens expirados o mal validados.
- Rutas sin protección.
- Roles mal aplicados.
- Acceso a recursos de otro tenant.
