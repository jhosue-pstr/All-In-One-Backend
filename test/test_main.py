import pytest


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_lifespan_runs_on_startup(client):
    response = client.get("/")
    assert response.status_code == 200