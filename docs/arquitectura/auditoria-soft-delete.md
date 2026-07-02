# Auditoría y soft delete

El backend incorpora dos mecanismos transversales importantes: **auditoría** y **soft delete**. Ambos fortalecen la trazabilidad y reducen riesgos de pérdida de información.

## Auditoría

La auditoría técnica consiste en registrar operaciones relevantes realizadas sobre entidades del sistema. El modelo de auditoría conserva datos como entidad afectada, identificador del registro, acción realizada, usuario responsable, valores anteriores, valores nuevos, fecha e IP de origen cuando corresponde.

| Campo | Uso |
|---|---|
| `entidad` | Tabla o recurso afectado. |
| `entidad_id` | Identificador del registro impactado. |
| `accion` | Tipo de operación: INSERT, UPDATE, DELETE u otra acción definida. |
| `usuario_id` | Usuario asociado a la operación. |
| `valores_anteriores` | Estado previo del registro. |
| `valores_nuevos` | Estado posterior del registro. |
| `fecha` | Momento de la operación. |
| `ip_origen` | Trazabilidad de red cuando está disponible. |

## Soft delete

El soft delete evita eliminar físicamente ciertos registros. En vez de borrar de la base de datos, se marca el registro como inactivo, eliminado o no visible. Esto permite conservar trazabilidad, recuperar información si fuera necesario y evitar pérdida accidental.

Ejemplos de uso observables en el backend:

- usuarios internos con campo de actividad;
- categorías y publicaciones de Blog con campos de eliminación lógica;
- filtros para no mostrar elementos eliminados o inactivos en endpoints públicos;
- separación entre vista pública y vista administrativa.

## Diferencia entre ambos mecanismos

| Mecanismo | Qué resuelve |
|---|---|
| Auditoría | Permite saber qué ocurrió, cuándo, sobre qué entidad y por quién. |
| Soft delete | Permite conservar registros aunque ya no sean visibles o activos. |

## Importancia para All-InOne

En una plataforma multitenant, estos controles son especialmente importantes porque existen múltiples sitios, usuarios, módulos y operaciones. Si una acción crítica no queda registrada, se pierde trazabilidad. Si un registro se elimina físicamente sin control, puede afectar reportes, historial o integridad funcional.

## Consideraciones de auditoría

La auditoría debe revisar:

- en qué entidades se aplica auditoría;
- qué acciones generan registros de auditoría;
- si se excluyen datos sensibles como contraseñas;
- si los endpoints filtran correctamente registros eliminados;
- si existe consistencia entre documentación, código y pruebas.

!!! info "Buena práctica observada"
    El registro de auditoría evita depender solo de logs temporales del servidor. Al estar modelado en base de datos, puede usarse como evidencia de operaciones relevantes.

<div class="defense-box" markdown>
**Frase para exposición:** “Auditoría y soft delete aportan trazabilidad y conservación de información; por eso son controles clave dentro del backend.”
</div>
