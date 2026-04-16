import pytest


def test_registro_success(client, user_data):
    response = client.post("/api/auth/registro", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["correo"] == user_data["correo"]


def test_registro_correo_existente(client, user_data):
    client.post("/api/auth/registro", json=user_data)

    response = client.post("/api/auth/registro", json=user_data)
    assert response.status_code == 400
    assert "ya esta registrado" in response.text


def test_inicio_success(client, user_data):
    client.post("/api/auth/registro", json=user_data)

    response = client.post(
        "/api/auth/inicio",
        data={
            "username": user_data["correo"],
            "password": user_data["contrasena"]
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_inicio_contrasena_incorrecta(client, user_data):
    client.post("/api/auth/registro", json=user_data)

    response = client.post(
        "/api/auth/inicio",
        data={
            "username": user_data["correo"],
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


def test_usuario_actual(client, user_data):
    client.post("/api/auth/registro", json=user_data)

    login_response = client.post(
        "/api/auth/inicio",
        data={
            "username": user_data["correo"],
            "password": user_data["contrasena"]
        }
    )

    print(f"Login status: {login_response.status_code}")
    print(f"Login body: {login_response.json()}")

    token = login_response.json()["access_token"]
    print(f"Token: {token}")

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    print(f"Me status: {response.status_code}")
    print(f"Me body: {response.json()}")

    assert response.status_code == 200
    data = response.json()
    assert data["correo"] == user_data["correo"]


def test_usuario_actual_sin_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
