import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities as activities_state

client = TestClient(app)
initial_activities = copy.deepcopy(activities_state)


@pytest.fixture(autouse=True)
def reset_activities():
    activities_state.clear()
    activities_state.update(copy.deepcopy(initial_activities))
    yield


def test_root_redirects_to_index_html():
    response = client.get("/", allow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_list():
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert "Programming Class" in response.json()
    assert isinstance(response.json(), dict)
    assert len(response.json()) >= 1


def test_signup_for_activity():
    payload = {"email": "newstudent@mergington.edu"}
    response = client.post("/activities/Basketball Team/signup", params=payload)

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up newstudent@mergington.edu for Basketball Team"
    assert "newstudent@mergington.edu" in activities_state["Basketball Team"]["participants"]


def test_signup_existing_student_returns_400():
    payload = {"email": "michael@mergington.edu"}
    response = client.post("/activities/Chess Club/signup", params=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_from_activity():
    payload = {"email": "michael@mergington.edu"}
    response = client.post("/activities/Chess Club/unregister", params=payload)

    assert response.status_code == 200
    assert response.json()["message"] == "Unregistered michael@mergington.edu from Chess Club"
    assert "michael@mergington.edu" not in activities_state["Chess Club"]["participants"]
