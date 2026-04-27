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
    # Arrange
    # (no setup needed, state is reset by fixture)

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_list():
    # Arrange
    # (activities are populated by fixture)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert "Programming Class" in response.json()
    assert isinstance(response.json(), dict)
    assert len(response.json()) >= 1


def test_signup_for_activity():
    # Arrange
    activity_name = "Basketball Team"
    email = "newstudent@mergington.edu"
    payload = {"email": email}

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=payload)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities_state[activity_name]["participants"]


def test_signup_existing_student_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    payload = {"email": email}

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=payload)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    payload = {"email": email}
    assert email in activities_state[activity_name]["participants"]  # verify precondition

    # Act
    response = client.post(f"/activities/{activity_name}/unregister", params=payload)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities_state[activity_name]["participants"]
