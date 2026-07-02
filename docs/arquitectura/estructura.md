# Estructura del repositorio backend

La estructura del backend está organizada para separar la entrada HTTP, la configuración central, la persistencia, los modelos, los esquemas, los servicios y los módulos funcionales. Esta organización permite ubicar rápidamente dónde se define una ruta, dónde se valida la información, dónde vive la lógica de negocio y dónde se representa la información en base de datos.

## Estructura general

```text
All-In-One-Backend-main/
├── app/
│   ├── api/                 # Routers principales del sistema
│   ├── core/                # Configuración, permisos y componentes base
│   ├── db/                  # Conexión, sesión y seeds iniciales
│   ├── models/              # Modelos base del dominio principal
│   ├── schemas/             # Esquemas Pydantic para entrada/salida
│   ├── service/             # Lógica de negocio del core
│   ├── packages/modulos/    # Módulos funcionales independientes
│   └── main.py              # Punto de entrada FastAPI
├── test/                    # Pruebas automatizadas con Pytest
├── k6/                      # Pruebas de rendimiento
├── zap/                     # Pruebas de seguridad OWASP ZAP
├── media/                   # Archivos públicos de plantillas/sitios
├── uploads/                 # Archivos cargados por módulos
├── static/                  # Recursos estáticos, widget público
├── Dockerfile
├── Jenkinsfile
├── requirements.txt
└── pytest.ini
```

## Lectura por capas

| Carpeta | Qué contiene | Importancia |
|---|---|---|
| `app/api` | Routers de autenticación, sitios, plantillas, módulos y roles. | Define la superficie HTTP principal del backend. |
| `app/packages/modulos` | Blog, Tienda, Analítica y Auth Público. | Encapsula funcionalidades de negocio por módulo. |
| `app/models` | Entidades SQLAlchemy del core. | Representa la estructura persistente principal. |
| `app/schemas` | Contratos Pydantic. | Controla entradas y respuestas de la API. |
| `app/service` | Reglas de negocio. | Evita que toda la lógica quede dentro de los endpoints. |
| `app/core` | Configuración, permisos y clases base. | Centraliza comportamiento transversal. |
| `test` | Pruebas unitarias/integración. | Evidencia calidad y validación técnica. |
| `k6` / `zap` | Rendimiento y seguridad. | Evidencia DevSecOps y revisión no funcional. |

## Punto de entrada

El archivo `app/main.py` cumple cuatro funciones importantes:

1. crea la aplicación FastAPI;
2. configura CORS para el entorno de desarrollo;
3. monta carpetas públicas como `media`, `uploads` y `static`;
4. registra routers principales y routers modulares.

Esta concentración en `main.py` ayuda a identificar rápidamente qué módulos forman parte de la API activa y permite contrastar la documentación con la implementación real.

## Evidencia para auditoría

La estructura del repositorio es una evidencia útil para varios puntos del checklist SDLC:

- control de versiones y organización del código;
- separación modular;
- trazabilidad entre módulos y endpoints;
- existencia de pruebas automatizadas;
- uso de herramientas de calidad y seguridad;
- documentación técnica generada para backend.

<div class="defense-box" markdown>
**Frase para exposición:** “La estructura del backend facilita la auditoría porque permite revisar por separado rutas, servicios, modelos, esquemas, pruebas y módulos.”
</div>
