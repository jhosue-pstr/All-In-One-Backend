from typing import Annotated
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db, Base
from app.api import (
    auth_router,
    sitio_router,
    sitio_modulo_router,
    modulo_router,
    plantilla_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.db.database import engine
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(modulo_router, prefix="/api")
app.include_router(sitio_router, prefix="/api")
app.include_router(sitio_modulo_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(plantilla_router, prefix="/api")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/health")
def health_check(db: Annotated[Session, Depends(get_db)]):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}