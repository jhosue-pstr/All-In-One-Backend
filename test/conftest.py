import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.db.database import Base, get_db


if os.path.exists("test.db"):
    os.remove("test.db")


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def _seed_roles_y_permisos_para_tests():
    """
    Crea roles/permisos y permite que el rol 'user' tenga permisos completos
    durante los tests antiguos.

    Esto evita que pruebas existentes fallen con 403 después de agregar RBAC.
    """
    from app.db.seed_roles import seed_roles
    from app.models.rol import Rol, Permiso, RolPermiso

    db = TestingSessionLocal()
    try:
        seed_roles(db)

        rol_user = db.query(Rol).filter(Rol.codigo == "user").first()

        if rol_user:
            permisos = db.query(Permiso).filter(Permiso.activo == True).all()

            permisos_actuales = {
                rp.permiso_id
                for rp in db.query(RolPermiso)
                .filter(RolPermiso.rol_id == rol_user.id)
                .all()
            }

            for permiso in permisos:
                if permiso.id not in permisos_actuales:
                    db.add(
                        RolPermiso(
                            rol_id=rol_user.id,
                            permiso_id=permiso.id,
                        )
                    )

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _hacer_usuario_super_admin(correo: str):
    from app.models.usuario import User

    db = TestingSessionLocal()
    try:
        user = db.query(User).filter(User.correo == correo).first()

        if user:
            user.role = "super_admin"
            user.activo = True
            db.commit()
    finally:
        db.close()


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    _seed_roles_y_permisos_para_tests()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(setup_db):
    """
    Cliente de pruebas.

    Además crea un usuario super_admin automático para que los endpoints
    protegidos puedan probarse sin fallar por 401 cuando los tests antiguos
    no envían Authorization.
    """
    test_client = TestClient(app)

    admin_data = {
        "correo": "admin-test@example.com",
        "contrasena": "123456",
        "nombre": "Admin",
        "apellido": "Test",
    }

    test_client.post("/api/auth/registro", json=admin_data)
    _hacer_usuario_super_admin(admin_data["correo"])

    login_response = test_client.post(
        "/api/auth/inicio",
        data={
            "username": admin_data["correo"],
            "password": admin_data["contrasena"],
        },
    )

    token = None

    if login_response.status_code == 200:
        token = login_response.json().get("access_token")

    original_request = test_client.request

    def request_with_default_auth(method, url, **kwargs):
        headers = dict(kwargs.pop("headers", {}) or {})

        url_text = str(url)

        es_ruta_auth = (
            url_text.startswith("/api/auth")
            or "/api/auth" in url_text
        )

        if token and not es_ruta_auth and "Authorization" not in headers:
            headers["Authorization"] = f"Bearer {token}"

        return original_request(
            method,
            url,
            headers=headers,
            **kwargs,
        )

    test_client.request = request_with_default_auth

    return test_client


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
        "apellido": "User",
    }


@pytest.fixture
def user(db):
    from app.models.usuario import User

    user = User(
        correo="test@example.com",
        contrasena="123456",
        nombre="Test",
        apellido="User",
        role="super_admin",
        activo=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture
def auth_headers(client, user_data):
    client.post("/api/auth/registro", json=user_data)
    _hacer_usuario_super_admin(user_data["correo"])

    login_response = client.post(
        "/api/auth/inicio",
        data={
            "username": user_data["correo"],
            "password": user_data["contrasena"],
        },
    )

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }