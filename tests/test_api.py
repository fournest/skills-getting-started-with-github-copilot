from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


def test_get_activities_initial():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # should contain some known activities
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "pytest.user@example.com"

    # Ensure not present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Signup
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")
    assert email in activities[activity]["participants"]

    # Duplicate signup should fail
    resp_dup = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp_dup.status_code == 400

    # Unregister
    resp_del = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp_del.status_code == 200
    assert email not in activities[activity]["participants"]


def test_signup_activity_not_found():
    resp = client.post("/activities/NonExisting/signup?email=a@b.com")
    assert resp.status_code == 404


def test_unregister_not_found():
    resp = client.delete("/activities/Chess%20Club/participants?email=not.present%40example.com")
    # Should return 404 for participant not found
    assert resp.status_code == 404
