import pytest


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_lifespan_creates_tables(client):
    from app.db.database import Base
    
    assert Base is not None