# Antecedentes del sistema All-InOne

## Descripción del sistema

**All-InOne** es una plataforma SaaS multitenant desarrollada por **ModularSoft - Grupo 4**. Su objetivo es ayudar a pequeñas y medianas empresas a crear y administrar presencia digital sin depender de múltiples herramientas separadas.

La plataforma integra dos grandes capacidades:

1. **Constructor visual de sitios web:** permite diseñar páginas mediante una interfaz drag-and-drop basada en GrapesJS.
2. **Motor modular de negocio:** permite activar funcionalidades como Blog, Tienda, Auth Público y Analítica según las necesidades de cada tenant o sitio.

## Componentes funcionales principales

| Componente | Función dentro del sistema |
|---|---|
| Sitios / tenants | Permiten separar la información y configuración de cada negocio. |
| Plantillas | Diseños reutilizables y clonables para acelerar la creación de sitios. |
| Constructor visual | Permite editar páginas sin programar. |
| Blog | Gestión de publicaciones, categorías, imágenes y estados. |
| Tienda | Gestión de productos, categorías, carrito, pedidos y checkout. |
| Auth Público | Registro e inicio de sesión de usuarios finales por sitio. |
| Analítica | Registro de visitas, eventos, sesiones y métricas. |
| Auditoría | Trazabilidad de operaciones relevantes. |
| Soft delete | Conservación lógica de registros importantes. |

## Arquitectura y tecnología

All-InOne adopta una **arquitectura de monolito modular**. Esto significa que no se divide en microservicios independientes, pero internamente organiza sus dominios funcionales como módulos separados.

| Capa / tecnología | Uso |
|---|---|
| Frontend | React, Vite y TypeScript. |
| Editor visual | GrapesJS. |
| Backend | FastAPI en Python. |
| Persistencia | SQLAlchemy y base de datos relacional. |
| Autenticación | JWT. |
| Autorización | Roles y permisos. |
| Calidad / DevSecOps | Jira, Jenkins, SonarCloud/SonarQube, Snyk, Playwright y k6. |

## Contexto de auditoría

La auditoría surge porque el sistema tiene una propuesta técnica amplia y múltiples evidencias: documentación, Jira, pruebas, seguridad, calidad, backend y frontend. Al existir tantos artefactos, se vuelve necesario verificar que todos sean coherentes entre sí.

!!! warning "Punto importante"
    La auditoría no asume que todo lo documentado está completamente implementado. Cada módulo debe contrastarse con evidencia real: código, rutas, servicios, componentes, pruebas y reportes.

## Frase clave

<div class="defense-box" markdown>

**“All-InOne no es una aplicación simple; por su arquitectura modular, multitenancy, editor visual y módulos de negocio, necesita una auditoría que valide coherencia entre documentación, implementación y pruebas.”**

</div>
