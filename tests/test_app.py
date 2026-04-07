"""
Tests for the Mergington High School Activities API.
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activity state after each test."""
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)


class TestActivities:
    def test_get_activities(self):
        # Arrange
        expected_activity = "Chess Club"

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert expected_activity in data
        assert "description" in data[expected_activity]
        assert "participants" in data[expected_activity]

    def test_activity_initial_participants(self):
        # Arrange
        activity_name = "Chess Club"

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert len(data[activity_name]["participants"]) == 2
        assert "michael@mergington.edu" in data[activity_name]["participants"]


class TestSignup:
    def test_signup_success(self):
        # Arrange
        activity_name = "Chess Club"
        new_email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email},
        )

        # Assert
        assert response.status_code == 200
        assert new_email in response.json()["message"]

        activities_response = client.get("/activities").json()
        assert new_email in activities_response[activity_name]["participants"]

    def test_signup_duplicate(self):
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email},
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity(self):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestUnregister:
    def test_unregister_success(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

        activities_response = client.get("/activities").json()
        assert email not in activities_response[activity_name]["participants"]

    def test_unregister_not_signed_up(self):
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_nonexistent_activity(self):
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRoot:
    def test_root_redirects_to_static_html(self):
        # Arrange
        expected_location = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert expected_location in response.headers["location"]
