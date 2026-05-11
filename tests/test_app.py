import copy
from urllib.parse import quote

from fastapi.testclient import TestClient

from src import app as app_module

INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)
client = TestClient(app_module.app)


def setup_function(function):
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def activity_url(activity_name: str) -> str:
    return f"/activities/{quote(activity_name, safe='')}/signup"


def test_get_activities_returns_expected_structure():
    # Arrange
    expected_keys = {"Chess Club", "Programming Class", "Gym Class"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert expected_keys.issubset(set(data.keys()))
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "teststudent@mergington.edu"
    assert email not in app_module.activities[activity_name]["participants"]

    # Act
    response = client.post(activity_url(activity_name), params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"
    first_response = client.post(activity_url(activity_name), params={"email": email})
    assert first_response.status_code == 200

    # Act
    duplicate_response = client.post(activity_url(activity_name), params={"email": email})

    # Assert
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student is already signed up for this activity"


def test_delete_participant_removes_registration():
    # Arrange
    activity_name = "Programming Class"
    email = "removeme@mergington.edu"
    signup_response = client.post(activity_url(activity_name), params={"email": email})
    assert signup_response.status_code == 200
    assert email in app_module.activities[activity_name]["participants"]

    # Act
    delete_response = client.delete(activity_url(activity_name), params={"email": email})

    # Assert
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]
