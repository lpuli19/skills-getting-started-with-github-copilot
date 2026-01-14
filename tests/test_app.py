"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Test the GET /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        """Test that activities list contains expected activities"""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Soccer Club",
            "Drama Club",
            "Art Studio",
            "Debate Team",
            "Science Club",
        ]
        
        for activity in expected_activities:
            assert activity in activities

    def test_get_activities_structure(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_details in activities.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_with_valid_activity_and_email(self):
        """Test signing up for an activity with valid data"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]

    def test_signup_adds_participant(self):
        """Test that signup actually adds the participant to the activity"""
        email = "signup_test@mergington.edu"
        
        # Sign up
        response = client.post(
            f"/activities/Programming%20Class/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities = client.get("/activities").json()
        assert email in activities["Programming Class"]["participants"]

    def test_signup_duplicate_email_returns_400(self):
        """Test that signing up twice with same email returns 400"""
        email = "duplicate_test@mergington.edu"
        
        # First signup
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup with same email
        response2 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self):
        """Test that signing up for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUnregisterFromActivity:
    """Test the POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_removes_participant(self):
        """Test that unregister removes the participant"""
        email = "unregister_test@mergington.edu"
        
        # First, sign up
        client.post(
            f"/activities/Soccer%20Club/signup?email={email}"
        )
        
        # Verify participant was added
        activities = client.get("/activities").json()
        assert email in activities["Soccer Club"]["participants"]
        
        # Unregister
        response = client.post(
            f"/activities/Soccer%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities = client.get("/activities").json()
        assert email not in activities["Soccer Club"]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self):
        """Test that unregistering from non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404

    def test_unregister_not_registered_returns_400(self):
        """Test that unregistering someone not registered returns 400"""
        response = client.post(
            "/activities/Drama%20Club/unregister?email=not_registered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_success_message(self):
        """Test that successful unregister returns correct message"""
        email = "unregister_msg_test@mergington.edu"
        
        # Sign up first
        client.post(
            f"/activities/Art%20Studio/signup?email={email}"
        )
        
        # Unregister
        response = client.post(
            f"/activities/Art%20Studio/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]


class TestRoot:
    """Test the root endpoint"""

    def test_root_redirects(self):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
