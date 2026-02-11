from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def register_and_login(email: str = "user@example.com", password: str = "Password123!"):
    response = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    if response.status_code == 400:
        response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_auth_and_conversation_flow():
    token = register_and_login()
    headers = {"Authorization": f"Bearer {token}"}

    create = client.post("/api/v1/conversations", headers=headers, json={"title": "Test Chat", "metadata": {"topic": "x"}})
    assert create.status_code == 200
    conversation_id = create.json()["id"]

    listing = client.get("/api/v1/conversations", headers=headers)
    assert listing.status_code == 200
    assert listing.json()["total"] >= 1

    message = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        headers=headers,
        json={"content": "Hello there"},
    )
    assert message.status_code == 200
    assert message.json()["role"] == "assistant"


def test_streaming_endpoint_returns_sse():
    token = register_and_login("stream@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    create = client.post("/api/v1/conversations", headers=headers, json={"title": "Stream Test"})
    conversation_id = create.json()["id"]

    with client.stream(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages/stream",
        headers=headers,
        json={"content": "Stream this please"},
    ) as response:
        assert response.status_code == 200
        body = "".join(chunk.decode("utf-8") if isinstance(chunk, bytes) else chunk for chunk in response.iter_text())
        assert "event: message_start" in body
        assert "event: message_stop" in body
