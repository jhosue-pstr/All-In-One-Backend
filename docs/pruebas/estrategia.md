# Estrategia de pruebas

La estrategia de pruebas del backend busca validar funcionalidad, estabilidad, rendimiento, seguridad y calidad del código.

## Tipos de pruebas considerados

| Tipo de prueba | Herramienta / evidencia | Objetivo |
|---|---|---|
| Pruebas automatizadas backend | Pytest | Validar endpoints, servicios y flujos principales. |
| Pruebas funcionales | Casos documentados | Verificar comportamiento esperado del sistema. |
| Pruebas de rendimiento | k6 | Medir tiempos de respuesta y comportamiento bajo carga. |
| Pruebas de seguridad | OWASP ZAP | Detectar vulnerabilidades dinámicas. |
| Análisis estático | SonarCloud / SonarQube | Revisar bugs, vulnerabilidades, duplicación y mantenibilidad. |
| Análisis de dependencias | Snyk | Detectar riesgos en librerías. |
| Integración continua | Jenkins | Automatizar tareas de validación. |

## Flujos críticos a validar

- Registro e inicio de sesión.
- Gestión de usuarios internos.
- Gestión de roles y permisos.
- Creación y administración de sitios.
- Activación de módulos por sitio.
- Gestión de plantillas.
- Blog: categorías y publicaciones.
- Tienda: productos, categorías, carrito y pedidos.
- Auth Público: usuarios finales por sitio.
- Analítica: visitas, eventos y dashboard.
- Auditoría y soft delete.

## Criterio de aceptación general

Una prueba se considera aceptable cuando:

- Tiene objetivo claro.
- Define entradas o escenario.
- Presenta resultado esperado.
- Registra resultado obtenido.
- Permite evidenciar si el flujo cumple o no cumple.
