# Configuración del backend

La configuración del backend permite adaptar la aplicación al entorno donde se ejecuta. Incluye parámetros de conexión, seguridad, CORS, archivos estáticos y documentación de API.

## Configuración principal

| Elemento | Descripción |
|---|---|
| Base de datos | Define URL de conexión usada por SQLAlchemy. |
| JWT | Usa clave secreta, algoritmo y tiempo de expiración. |
| CORS | Permite comunicación con frontend local. |
| Media | Expone archivos relacionados con plantillas y sitios. |
| Uploads | Expone archivos cargados por módulos. |
| Static | Expone recursos estáticos del sistema. |

## CORS

El backend permite orígenes de desarrollo como `localhost` para integrar con el frontend Vite. Esto es útil durante pruebas, pero debe revisarse antes de un entorno productivo.

```mermaid
flowchart LR
    F[Frontend local] -->|CORS permitido| B[FastAPI Backend]
```

## Archivos públicos

| Ruta montada | Carpeta | Uso |
|---|---|---|
| `/media` | `media/` | Miniaturas o recursos de plantillas y sitios. |
| `/uploads` | `uploads/` | Imágenes cargadas desde módulos. |
| `/static` | `static/` | Recursos estáticos como widget público. |

## Configuración inicial

En el arranque, el backend puede crear tablas y cargar seeds de módulos, roles y plantillas. Esto ayuda a tener un entorno funcional de prueba sin configuración manual excesiva.

## Recomendaciones

- usar variables de entorno para secretos;
- no subir claves reales al repositorio;
- revisar CORS antes de producción;
- separar configuración local, pruebas y producción;
- documentar cambios de configuración;
- mantener actualizada la guía de instalación.

<div class="defense-box" markdown>
**Frase para exposición:** “La configuración del backend permite ejecutar el sistema en pruebas y documentar variables críticas, pero requiere endurecimiento si se llevara a producción real.”
</div>
