# Estructura del repositorio

La estructura del backend está organizada para separar API, modelos, esquemas, servicios, configuración, pruebas y módulos funcionales.

```text
All-In-One-Backend/
├─ app/
│  ├─ api/
│  ├─ core/
│  ├─ db/
│  ├─ models/
│  ├─ packages/
│  │  └─ modulos/
│  ├─ schemas/
│  ├─ service/
│  └─ main.py
├─ k6/
├─ media/
├─ static/
├─ test/
├─ uploads/
├─ zap/
├─ Dockerfile
├─ Jenkinsfile
├─ docker-compose.k6.yml
├─ docker-compose.zap.yml
├─ pytest.ini
├─ requirements.txt
└─ requirements.lock
```

## Carpetas principales

| Carpeta / archivo | Descripción |
|---|---|
| `app/main.py` | Punto de entrada de la aplicación FastAPI. Registra middleware, rutas y carpetas estáticas. |
| `app/api/` | Routers principales del sistema: autenticación, sitios, módulos, plantillas, roles, auth público. |
| `app/core/` | Configuración general, permisos, middleware y elementos base. |
| `app/db/` | Configuración de base de datos y scripts de seed. |
| `app/models/` | Modelos principales del sistema. |
| `app/schemas/` | Esquemas Pydantic para entrada y salida de datos. |
| `app/service/` | Lógica de negocio de componentes principales. |
| `app/packages/modulos/` | Módulos funcionales como Blog, Tienda, Analítica y Auth Público. |
| `test/` | Pruebas automatizadas del backend. |
| `k6/` | Pruebas de rendimiento. |
| `zap/` | Evidencias o configuración relacionada con pruebas de seguridad. |
| `media/`, `uploads/`, `static/` | Recursos públicos y archivos servidos por el backend. |

## Observación de auditoría

La estructura refleja un enfoque de **monolito modular**, ya que los módulos están dentro del mismo backend, pero se separan por dominios funcionales.
