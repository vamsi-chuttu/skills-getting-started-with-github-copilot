import src.app as app_module
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def activities(monkeypatch):
    activities = {
        "Robotics Club": {
            "description": "Build and program robots",
            "schedule": "Wednesdays, 3:30 PM - 4:30 PM",
            "max_participants": 3,
            "participants": ["existing@mergington.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return activities


@pytest.fixture
def client(activities):
    return TestClient(app_module.app)


def test_get_activities_returns_current_activities(client, activities):
    # Arrange
    expected_activities = activities

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client, activities):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post(
        "/activities/Robotics Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Robotics Club"}
    assert activities["Robotics Club"]["participants"] == [
        "existing@mergington.edu",
        email,
    ]


def test_signup_rejects_duplicate_participant(client, activities):
    # Arrange
    email = "existing@mergington.edu"
    original_participants = activities["Robotics Club"]["participants"].copy()

    # Act
    response = client.post(
        "/activities/Robotics Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert activities["Robotics Club"]["participants"] == original_participants


def test_signup_returns_not_found_for_unknown_activity(client, activities):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert activities["Robotics Club"]["participants"] == [
        "existing@mergington.edu"
    ]


def test_unregister_removes_participant(client, activities):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Robotics Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Robotics Club"
    }
    assert activities["Robotics Club"]["participants"] == []


def test_unregister_returns_not_found_for_unknown_activity(client, activities):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Unknown Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert activities["Robotics Club"]["participants"] == [
        "existing@mergington.edu"
    ]


def test_unregister_returns_not_found_for_unsigned_participant(client, activities):
    # Arrange
    email = "not-signed-up@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Robotics Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert activities["Robotics Club"]["participants"] == [
        "existing@mergington.edu"
    ]