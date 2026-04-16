from typing import Annotated
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db, Base
from app.models.usuario import User
from app.api.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.db.database import engine
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/api")


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
