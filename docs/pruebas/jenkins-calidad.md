# Jenkins y calidad

El backend incluye un `Jenkinsfile`, lo que permite documentar un flujo de integración continua para validar el proyecto.

## Archivo principal

```text
Jenkinsfile
```

## Propósito de Jenkins

Jenkins puede usarse para automatizar:

- Instalación de dependencias.
- Ejecución de pruebas.
- Análisis de calidad.
- Integración con herramientas externas.
- Generación de evidencias técnicas.

## Herramientas relacionadas

| Herramienta | Uso |
|---|---|
| Pytest | Pruebas automatizadas. |
| SonarCloud / SonarQube | Análisis estático y métricas de calidad. |
| Snyk | Análisis de dependencias y vulnerabilidades. |
| k6 | Rendimiento. |
| OWASP ZAP | Seguridad dinámica. |

## Consideración importante

El flujo documentado corresponde a integración y validación técnica en entorno académico/de prueba. No implica necesariamente un despliegue productivo formal.
