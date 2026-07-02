# Instalación local

Esta guía resume el proceso de preparación del backend en un entorno local o académico.

## Requisitos previos

- Python instalado.
- Git instalado.
- Acceso al repositorio backend.
- Entorno virtual configurado.
- Dependencias del proyecto disponibles en `requirements.txt`.

## Pasos generales

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio-backend>
cd <repositorio-backend>

# 2. Crear entorno virtual
python -m venv .venv

# 3. Activar entorno virtual en Windows
.venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt
```

## Ejecución del backend

La ejecución concreta puede variar según la configuración del proyecto, variables de entorno y base de datos utilizada.

```bash
uvicorn app.main:app --reload
```

## Validación inicial

Después de iniciar el backend, se recomienda validar:

- Que el servidor responda correctamente.
- Que Swagger/OpenAPI esté disponible.
- Que los endpoints críticos respondan.
- Que la conexión a la base de datos funcione.
- Que la autenticación y permisos puedan probarse.

!!! warning "Importante"
    Este procedimiento corresponde a instalación de prueba. No equivale a un procedimiento formal de despliegue productivo.
