# Guía de mantenimiento técnico

Esta guía resume cómo debería mantenerse el backend para futuras versiones. Su objetivo es que el equipo pueda agregar módulos, corregir defectos o mejorar seguridad sin romper la estructura existente.

## Principios de mantenimiento

| Principio | Aplicación práctica |
|---|---|
| Separar responsabilidades | No concentrar reglas de negocio complejas dentro de los routers. |
| Mantener trazabilidad | Relacionar cambios con Jira, commits, pruebas y documentación. |
| Proteger datos por sitio | Toda funcionalidad multitenant debe filtrar por `site_id` o `sitio_id`. |
| Documentar endpoints | Mantener descripciones claras en FastAPI/Swagger y MkDocs. |
| Probar antes de integrar | Ejecutar Pytest y pruebas relevantes antes de hacer push. |
| Evitar deuda técnica | Refactorizar duplicaciones y mantener nombres consistentes. |

## Agregar un nuevo módulo

Para incorporar un módulo futuro, se recomienda seguir este flujo:

```text
1. Definir requisito e historia de usuario.
2. Crear modelo de datos si requiere persistencia.
3. Crear schemas Pydantic de entrada y salida.
4. Crear servicios con reglas de negocio.
5. Crear rutas FastAPI del módulo.
6. Registrar router en app/main.py si corresponde.
7. Agregar permisos en seed de roles/permisos.
8. Crear pruebas unitarias o de API.
9. Actualizar MkDocs y evidencias SDLC.
```

## Checklist técnico antes de cerrar un cambio

- [ ] El endpoint aparece en Swagger.
- [ ] El módulo respeta autenticación y permisos cuando corresponde.
- [ ] Las consultas multitenant filtran por sitio.
- [ ] No se exponen datos sensibles.
- [ ] Se manejan errores HTTP claros.
- [ ] Existen pruebas asociadas al cambio.
- [ ] Se actualizó la documentación técnica.
- [ ] El cambio queda trazado en Jira/GitHub.

## Riesgos frecuentes

| Riesgo | Prevención |
|---|---|
| Mezclar lógica en rutas | Mover reglas repetidas a servicios. |
| Romper aislamiento por tenant | Revisar consultas y parámetros de sitio. |
| Omitir permisos | Usar dependencias de autorización en rutas críticas. |
| Documentar algo no implementado | Separar implementado, parcial y planificado. |
| Falta de pruebas | Agregar casos mínimos por flujo crítico. |

<div class="decision-box" markdown>
**Buena práctica:** cada cambio técnico debería dejar tres evidencias: código actualizado, prueba asociada y documentación ajustada.
</div>
