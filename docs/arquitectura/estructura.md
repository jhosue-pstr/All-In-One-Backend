# Estructura del repositorio backend

La estructura del backend está organizada para separar aplicación, pruebas, evidencias y recursos estáticos.

```text
BACKEND/
├─ app/
├─ k6/
├─ media/
├─ static/
├─ test/
├─ uploads/
├─ zap/
├─ Dockerfile
├─ Jenkinsfile
├─ requirements.txt
├─ pytest.ini
├─ docker-compose.k6.yml
└─ docker-compose.zap.yml
```

## Carpetas principales

| Carpeta / archivo | Propósito |
|---|---|
| `app/` | Código principal del backend. |
| `test/` | Pruebas del backend. |
| `k6/` | Scripts o recursos para pruebas de rendimiento. |
| `zap/` | Evidencias o configuración relacionada con pruebas de seguridad. |
| `media/`, `uploads/`, `static/` | Archivos estáticos, imágenes o recursos cargados. |
| `Dockerfile` | Construcción del contenedor del backend. |
| `Jenkinsfile` | Pipeline de integración continua. |

!!! info "Uso en auditoría"
    Esta estructura sirve como evidencia para revisar organización, pruebas, seguridad y mantenibilidad del backend.
