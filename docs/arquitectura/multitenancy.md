# Multitenancy

All-InOne se plantea como una plataforma **SaaS multitenant**, donde distintos negocios o sitios pueden usar la misma plataforma manteniendo su información separada.

## Concepto

Un tenant representa un sitio, empresa o cliente dentro de la plataforma.

## Riesgo principal

El riesgo más importante es el acceso cruzado entre tenants, es decir, que un usuario de un sitio pueda ver o modificar información de otro.

## Controles esperados

- Asociar registros a un sitio o tenant.
- Validar permisos antes de acceder a recursos.
- Filtrar consultas por tenant.
- Proteger endpoints críticos.
- Registrar acciones relevantes mediante auditoría.

!!! warning "Revisión crítica"
    En auditoría, el multitenancy debe revisarse con especial atención porque impacta directamente en seguridad y confidencialidad.
