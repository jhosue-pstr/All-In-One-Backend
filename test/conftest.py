import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db

sys.path.insert(0, str(Path(__file__).parent.parent))

if os.path.exists("test.db"):
    os.remove("test.db")

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client(setup_db):
    return TestClient(app)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def user_data():
    return {
        "correo": "test@example.com",
        "contrasena": "123456",
        "nombre": "Test",
        "apellido": "User"
    }


@pytest.fixture
def user(db):
    from app.models.usuario import User
    user = User(
        correo="test@example.com",
        contrasena="123456",
        nombre="Test",
        apellido="User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
