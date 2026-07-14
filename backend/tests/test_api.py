import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    resp = client.post("/api/auth/register", json={"username": "testuser", "password": "testpass123"})
    resp = client.post(
        "/api/auth/token",
        data={"username": "testuser", "password": "testpass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return resp.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_health_check(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["app"] == "DocMind"


def test_register_and_login(client):
    resp = client.post("/api/auth/register", json={"username": "newuser", "password": "newpass123"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "newuser"

    resp = client.post(
        "/api/auth/token",
        data={"username": "newuser", "password": "newpass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_register_duplicate(client):
    client.post("/api/auth/register", json={"username": "dupuser", "password": "pass123"})
    resp = client.post("/api/auth/register", json={"username": "dupuser", "password": "pass123"})
    assert resp.status_code == 400


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={"username": "wrongpw", "password": "pass123"})
    resp = client.post(
        "/api/auth/token",
        data={"username": "wrongpw", "password": "wrong"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 401


def test_me_with_token(client, auth_token):
    resp = client.get("/api/auth/me", headers=auth_headers(auth_token))
    assert resp.status_code == 200
    assert resp.json()["username"] == "testuser"


def test_me_without_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_list_documents(client, auth_token):
    resp = client.get("/api/documents", headers=auth_headers(auth_token))
    assert resp.status_code == 200


def test_list_history(client, auth_token):
    resp = client.get("/api/history", headers=auth_headers(auth_token))
    assert resp.status_code == 200


def test_chat_empty_question(client, auth_token):
    resp = client.post("/api/chat", json={"question": ""}, headers=auth_headers(auth_token))
    assert resp.status_code == 400


def test_search_empty_question(client, auth_token):
    resp = client.post("/api/search", json={"question": ""}, headers=auth_headers(auth_token))
    assert resp.status_code == 400