# Visión general de arquitectura

All-InOne utiliza una arquitectura de **monolito modular**.

Esto significa que el sistema se mantiene como una sola aplicación backend, pero internamente se organiza por módulos y responsabilidades.

## Por qué monolito modular

Este enfoque permite:

- Mantener el proyecto simple para un contexto académico.
- Separar funcionalidades por dominios.
- Facilitar el mantenimiento.
- Evitar la complejidad de microservicios.
- Permitir crecimiento progresivo por módulos.

## Componentes principales

- Core Platform.
- Gestión de sitios o tenants.
- Plantillas.
- Módulos activables.
- Blog.
- Tienda.
- Auth Público.
- Analítica.
- Auditoría.
- Soft delete.

<div class="decision-box" markdown>
**Decisión arquitectónica:** se eligió monolito modular porque permite separar responsabilidades sin asumir la complejidad operativa de una arquitectura distribuida.
</div>
