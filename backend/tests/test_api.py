import os

os.environ["DATABASE_URL"] = "sqlite:///./test-commonground.db"
os.environ["SECRET_KEY"] = "test-secret"

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def auth(username: str, email: str) -> dict[str, str]:
    response = client.post("/api/auth/register", json={"username": username, "email": email, "password": "password123"})
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_member_can_create_and_change_vote():
    headers = auth("voter", "voter@example.com")
    community = client.post("/api/communities", json={"name": "Voting Club", "description": "Decisions"}, headers=headers)
    proposal = client.post(f"/api/communities/{community.json()['id']}/proposals", json={"title": "New event", "description": "Discuss it"}, headers=headers)
    proposal_id = proposal.json()["id"]

    first = client.put(f"/api/proposals/{proposal_id}/vote", json={"value": 1}, headers=headers)
    changed = client.put(f"/api/proposals/{proposal_id}/vote", json={"value": -1}, headers=headers)

    assert first.status_code == 200
    assert changed.json()["results"] == {"upvotes": 0, "downvotes": 1, "total": 1}


def test_non_member_cannot_vote():
    owner_headers = auth("owner", "owner@example.com")
    outsider_headers = auth("outsider", "outsider@example.com")
    community = client.post("/api/communities", json={"name": "Private Club", "description": "Members"}, headers=owner_headers)
    proposal = client.post(f"/api/communities/{community.json()['id']}/proposals", json={"title": "Question", "description": "Vote"}, headers=owner_headers)

    response = client.put(f"/api/proposals/{proposal.json()['id']}/vote", json={"value": 1}, headers=outsider_headers)

    assert response.status_code == 403
