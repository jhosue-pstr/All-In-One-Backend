from app.api.auth import router as auth_router
from app.api.sitio import router as sitio_router
from app.api.sitio_modulo import router as sitio_modulo_router
from app.api.modulo import router as modulo_router
from app.api.plantilla import router as plantilla_router

__all__ = [
    "auth_router",
    "sitio_router",
    "sitio_modulo_router",
    "modulo_router",
    "plantilla_router",
]