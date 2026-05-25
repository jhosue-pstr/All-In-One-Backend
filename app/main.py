from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated
import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import Base, get_db

import app.models  # noqa: F401

from app.api import (
    auth_router,
    sitio_router,
    sitio_modulo_router,
    modulo_router,
    plantilla_router,
    site_auth_router,
)

from app.api.publico import router as publico_router

from app.packages.modulos.blog.routes import router as blog_router
from app.packages.modulos.store.routes import router as store_router


@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover
    from app.db.database import engine
    from app.db.seed_modulos import seed_modulos

    Base.metadata.create_all(bind=engine)
    seed_modulos()

    for route in app.routes:
        if hasattr(route, "path"):
            print(f"Ruta cargada: {route.path}")

    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/health")
def health_check(db: Annotated[Session, Depends(get_db)]):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }


# =========================
# Carpetas públicas
# =========================

media_dir = Path("media")
media_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")

uploads_dir = Path("uploads")
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

static_dir = Path("static")
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


# =========================
# Routers API principales
# =========================

app.include_router(modulo_router, prefix="/api")
app.include_router(sitio_router, prefix="/api")
app.include_router(sitio_modulo_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(site_auth_router, prefix="/api")
app.include_router(plantilla_router, prefix="/api")


# =========================
# Routers de módulos
# =========================

app.include_router(blog_router, prefix="/api")
app.include_router(store_router)


# =========================
# Router público
# Siempre al final
# =========================

app.include_router(publico_router)


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    api_host = os.getenv("API_HOST", "127.0.0.1")
    uvicorn.run("app.main:app", host=api_host, port=8000, reload=True)