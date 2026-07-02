# All-InOne Backend

Bienvenido a la documentación del **backend de All-InOne**, una plataforma SaaS multitenant desarrollada por **ModularSoft - Grupo 4**.

Desde esta página puedes ingresar a dos bloques principales: la documentación técnica del backend y la documentación de auditoría SDLC basada en el Project Charter.

<div class="grid cards" markdown>

-   :material-server: **Documentación del Backend**

    Arquitectura, estructura del repositorio, API, seguridad, pruebas, calidad y despliegue de prueba del backend.

    [Ver backend](arquitectura/vision-general.md)

-   :material-clipboard-check: **Auditoría SDLC**

    Project Charter, criterios, metodología, riesgos, checklist SDLC, entregables y limitaciones de la auditoría.

    [Ver auditoría](auditoria/index.md)

</div>

!!! info "Alcance de esta documentación"
    Esta documentación describe el backend como parte de un proyecto académico. El sistema cuenta con despliegue y evidencias técnicas de prueba, pero no representa una implementación productiva formal para una empresa real.

## ¿Qué contiene la documentación del backend?

- Arquitectura de monolito modular.
- Estructura del backend.
- API y endpoints principales.
- Seguridad, JWT, roles y permisos.
- Multitenancy por sitio o tenant.
- Pruebas con Pytest, k6, OWASP ZAP y herramientas de calidad.
- Despliegue técnico de prueba.

## ¿Qué contiene la auditoría SDLC?

- Project Charter de Auditoría SDLC.
- Objetivos, alcance y exclusiones.
- Criterios de auditoría.
- Metodología de auditoría.
- Entregables y stakeholders.
- Cronograma y presupuesto estimado.
- Riesgos, factores críticos, supuestos y restricciones.
- Checklist SDLC aplicado al proyecto.

## Lectura recomendada

Para entender el sitio rápidamente, revisar en este orden:

1. [Visión general del backend](arquitectura/vision-general.md)
2. [Estructura del repositorio](arquitectura/estructura.md)
3. [Resumen de endpoints](api/resumen-endpoints.md)
4. [Controles de seguridad](seguridad/controles.md)
5. [Auditoría SDLC](auditoria/index.md)
6. [Checklist SDLC](auditoria/checklist-sdlc.md)
