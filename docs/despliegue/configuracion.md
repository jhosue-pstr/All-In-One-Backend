# Variables y configuración

El backend utiliza configuración centralizada para ejecutar la aplicación y conectarse con sus dependencias.

## Archivos relacionados

| Archivo | Descripción |
|---|---|
| `app/core/config.py` | Configuración principal del sistema. |
| `app/db/database.py` | Conexión y sesión de base de datos. |
| `requirements.txt` | Dependencias principales. |
| `requirements.lock` | Dependencias congeladas o bloqueadas. |
| `pytest.ini` | Configuración de pruebas. |

## CORS

El backend configura CORS para permitir comunicación con entornos frontend de desarrollo como:

```text
http://localhost:5173
http://127.0.0.1:5173
http://localhost:8000
```

## Carpetas públicas

Durante la ejecución se montan carpetas públicas:

| Ruta pública | Carpeta |
|---|---|
| `/media` | `media/` |
| `/uploads` | `uploads/` |
| `/static` | `static/` |

## Recomendación

Para un entorno productivo real se deberían documentar formalmente variables de entorno, secretos, origen CORS permitido, estrategia de base de datos, backups y monitoreo.
