# Instalación local

Esta sección describe una instalación local referencial del backend para fines de desarrollo, validación técnica y revisión académica.

!!! warning "Entorno de prueba"
    Los pasos descritos corresponden a un entorno local o de prueba. No equivalen a un procedimiento formal de puesta en producción.

## Requisitos previos

Antes de ejecutar el backend se recomienda contar con:

- Python instalado.
- Git instalado.
- Acceso al repositorio del backend.
- Entorno virtual de Python.
- Dependencias definidas en `requirements.txt`.

## Estructura inicial esperada

```text
All-In-One-Backend/
├─ app/
├─ k6/
├─ media/
├─ static/
├─ test/
├─ uploads/
├─ zap/
├─ Dockerfile
├─ Jenkinsfile
├─ pytest.ini
├─ requirements.txt
└─ requirements.lock
```

## Pasos de instalación

### 1. Clonar el repositorio

```bash
git clone URL_DEL_REPOSITORIO_BACKEND
cd NOMBRE_DEL_REPOSITORIO_BACKEND
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
```

En Windows PowerShell:

```bash
.\.venv\Scripts\Activate.ps1
```

En CMD:

```bash
.venv\Scripts\activate.bat
```

### 3. Instalar dependencias

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Ejecutar el backend

```bash
uvicorn app.main:app --reload
```

Por defecto, la API queda disponible en:

```text
http://127.0.0.1:8000
```

## Verificación rápida

| Recurso | URL |
|---|---|
| Raíz del backend | `http://127.0.0.1:8000/` |
| Health check | `http://127.0.0.1:8000/health` |
| Swagger/OpenAPI | `http://127.0.0.1:8000/docs` |

## Resultado esperado

Al consultar `/health`, el backend debe responder si el servicio y la base de datos están disponibles.

```json
{
  "status": "healthy",
  "database": "connected"
}
```

## Consideraciones

- El backend crea carpetas públicas como `media`, `uploads` y `static` si no existen.
- Durante el inicio se cargan datos semilla para módulos, roles y plantillas.
- La documentación OpenAPI generada por FastAPI es una evidencia útil para auditoría técnica.
