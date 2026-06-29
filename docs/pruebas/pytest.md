# Pytest

El backend incluye pruebas automatizadas en la carpeta `test/`.

## Ubicación

```text
test/
├─ api/
│  ├─ test_auth.py
│  ├─ test_blog.py
│  ├─ test_modulo.py
│  ├─ test_plantilla.py
│  ├─ test_analitica.py
│  └─ test_cobertura_final.py
└─ ...
```

## Ejecutar pruebas

Desde la raíz del backend:

```bash
pytest
```

Para ver resultados más detallados:

```bash
pytest -v
```

## Archivo de configuración

El archivo `pytest.ini` centraliza la configuración de pruebas.

## Qué valida Pytest

- Endpoints principales.
- Reglas funcionales del backend.
- Respuestas HTTP esperadas.
- Validaciones de módulos.
- Flujos de autenticación.
- Funcionalidad de Blog, Plantillas, Módulos y Analítica.

## Recomendación

Antes de publicar cambios importantes, se debe ejecutar Pytest y conservar evidencia del resultado como parte de la trazabilidad del desarrollo.
