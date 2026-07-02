# Pytest

Pytest se utiliza para validar el comportamiento del backend mediante pruebas organizadas por API, servicios, modelos, esquemas, base de datos y componentes transversales.

## Configuración

El archivo `pytest.ini` define criterios de descubrimiento de pruebas, modo asíncrono y rutas de test. Esto permite mantener un estándar mínimo para ejecutar la suite sin depender de comandos improvisados.

```text
pytest.ini
└── testpaths = test
```

## Organización

| Carpeta | Qué prueba |
|---|---|
| `test/api` | Endpoints REST y respuestas HTTP. |
| `test/service` | Reglas de negocio por dominio. |
| `test/db` | Conexión, seeds y persistencia. |
| `test/models` | Modelos y relaciones. |
| `test/schemas` | Validaciones Pydantic. |
| `test/core` | Middleware o componentes base. |

## Módulos con pruebas observables

El backend incluye pruebas para autenticación, sitios, plantillas, módulos, roles, Blog, Tienda, Analítica, Auth Público y relaciones sitio-módulo. Esto permite defender que los flujos principales cuentan con evidencia técnica.

## Comandos sugeridos

```bash
pytest
pytest --cov=app
pytest test/api
pytest test/service
```

## Qué evidencia aporta

- existencia de pruebas automatizadas;
- validación de endpoints críticos;
- detección temprana de errores;
- soporte para integración continua;
- trazabilidad entre código, módulos y resultados.

## Límites

Las pruebas automatizadas no sustituyen pruebas manuales, E2E completas ni validación formal en producción. Además, la cobertura debe interpretarse según los escenarios realmente probados.

<div class="defense-box" markdown>
**Frase para exposición:** “Pytest evidencia que el backend fue validado por capas: API, servicios, modelos, esquemas y base de datos.”
</div>
