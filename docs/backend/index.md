# Documentación Backend

<div class="hero" markdown>
# All-InOne Backend

<span class="badge">FastAPI</span>
<span class="badge">Python</span>
<span class="badge">SQLAlchemy</span>
<span class="badge">JWT</span>
<span class="badge">RBAC</span>
<span class="badge">Monolito Modular</span>

Esta sección describe la parte servidora de **All-InOne**, responsable de exponer la API, administrar la autenticación, aplicar permisos, gestionar sitios y módulos, conservar datos en una base relacional y sostener los controles transversales de auditoría y soft delete.

A diferencia de una documentación mínima de instalación, este apartado explica **cómo está construido el backend**, qué responsabilidades tiene cada capa, qué módulos atiende, qué evidencias técnicas existen y qué límites deben considerarse en el contexto académico del proyecto.
</div>

## Propósito del backend

El backend funciona como el núcleo lógico de la plataforma. Desde aquí se administran los usuarios internos, los sitios o tenants, las plantillas, los módulos activables y las funcionalidades de negocio como Blog, Tienda, Auth Público y Analítica.

Su responsabilidad no se limita a responder solicitudes HTTP. También concentra reglas de negocio, validaciones, control de acceso, aislamiento de información por sitio, carga de datos iniciales, exposición de archivos estáticos, documentación automática mediante Swagger/OpenAPI y generación de evidencia útil para pruebas, calidad y auditoría SDLC.

<div class="kpi-grid" markdown>
<div class="kpi-card" markdown>
<strong>API</strong>
Endpoints REST para administración, módulos y uso público.
</div>
<div class="kpi-card" markdown>
<strong>Seguridad</strong>
JWT, permisos, roles y rutas protegidas por dependencia.
</div>
<div class="kpi-card" markdown>
<strong>Datos</strong>
Modelos SQLAlchemy y persistencia relacional por entidades.
</div>
<div class="kpi-card" markdown>
<strong>Auditoría</strong>
Registro de acciones relevantes y conservación lógica de datos.
</div>
</div>

## Qué cubre esta documentación

<div class="section-grid" markdown>
<div class="section-card" markdown>
### Arquitectura
Explica el enfoque de monolito modular, la organización por capas, la relación entre rutas, servicios, esquemas y modelos, y la forma en que los módulos se integran al backend principal.
</div>
<div class="section-card" markdown>
### API
Resume los grupos de endpoints disponibles: autenticación interna, gestión de sitios, plantillas, módulos, roles, Blog, Tienda, Auth Público y Analítica.
</div>
<div class="section-card" markdown>
### Seguridad
Describe los mecanismos de autenticación, autorización, permisos, protección de rutas, aislamiento por sitio y riesgos técnicos relevantes.
</div>
<div class="section-card" markdown>
### Pruebas y calidad
Presenta la estrategia de validación con Pytest, k6, OWASP ZAP, Jenkins y herramientas de calidad usadas como evidencia técnica.
</div>
</div>

## Lectura recomendada

Para entender el backend de forma ordenada, se recomienda revisar primero la **visión general de arquitectura**, luego la **estructura del repositorio**, después los **módulos y endpoints**, y finalmente las páginas de **pruebas, seguridad y evidencias SDLC**.

<div class="decision-box" markdown>
**Idea clave para exposición:** el backend de All-InOne no es solo una API aislada; es el componente que sostiene la lógica central de la plataforma SaaS multitenant, organiza los módulos de negocio y aporta evidencia técnica para demostrar el ciclo de vida del desarrollo.
</div>
