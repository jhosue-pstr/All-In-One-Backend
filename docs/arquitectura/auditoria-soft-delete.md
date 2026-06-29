# Auditoría y soft delete

El backend contempla mecanismos transversales para mejorar la trazabilidad y preservar información importante.

## Auditoría

La auditoría permite registrar acciones relevantes realizadas en el sistema. Su utilidad principal es dejar evidencia de operaciones críticas para revisión posterior.

### Acciones que deberían auditarse

- Creación de registros importantes.
- Modificación de datos críticos.
- Eliminación lógica de entidades.
- Cambios de roles o permisos.
- Activación o desactivación de módulos.
- Operaciones administrativas sobre sitios.

## Soft delete

El **soft delete** consiste en marcar un registro como eliminado sin borrarlo físicamente de la base de datos.

```text
Eliminación física:
Registro desaparece de la base de datos.

Soft delete:
Registro se conserva, pero queda marcado como inactivo/eliminado.
```

## Beneficios

| Beneficio | Explicación |
|---|---|
| Trazabilidad | Permite saber qué ocurrió con un registro. |
| Recuperación | Facilita restaurar información si fue eliminada por error. |
| Auditoría | Mantiene evidencia para revisiones posteriores. |
| Seguridad | Reduce el riesgo de pérdida irreversible de datos. |

## Evidencia esperada

Para validar auditoría y soft delete se deben revisar:

- Modelos con campos de estado o eliminación lógica.
- Servicios que no eliminen físicamente cuando corresponde.
- Registros de auditoría en operaciones críticas.
- Pruebas que validen el comportamiento esperado.
