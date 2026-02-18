"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    
    # Save initial state
    initial_state = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice teamwork and compete in inter-school basketball matches",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Develop soccer skills through drills, scrimmages, and tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["ava@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore drawing, painting, and mixed media art projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["mia@mergington.edu", "charlotte@mergington.edu"]
        },
        "Drama Club": {
            "description": "Practice acting, stage presence, and perform school productions",
            "schedule": "Fridays, 3:30 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
        },
        "Debate Team": {
            "description": "Build critical thinking and public speaking through structured debates",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["elijah@mergington.edu", "james@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design, build, and program robots for challenges and competitions",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 12,
            "participants": ["benjamin@mergington.edu", "lucas@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Reset activities to initial state
    activities.clear()
    activities.update(initial_state)
    
    yield
    
    # Reset again after test
    activities.clear()
    activities.update(initial_state)


class TestGetActivities:
    """Test the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, reset_activities):
        """Should return all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Basketball Team" in data
        assert len(data) == 9
    
    def test_activity_has_required_fields(self, reset_activities):
        """Each activity should have required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, reset_activities):
        """Should successfully sign up a new participant"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant_to_activity(self, reset_activities):
        """Signup should add participant to the activity's participant list"""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        
        response = client.get("/activities")
        activity = response.json()["Chess Club"]
        assert email in activity["participants"]
    
    def test_signup_duplicate_participant_fails(self, reset_activities):
        """Signing up twice should return an error"""
        email = "michael@mergington.edu"  # Already signed up
        response = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity_fails(self, reset_activities):
        """Signing up for non-existent activity should fail"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_increments_participant_count(self, reset_activities):
        """Signup should increment the participant count"""
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
        
        response = client.get("/activities")
        new_count = len(response.json()["Chess Club"]["participants"])
        assert new_count == initial_count + 1


class TestUnregisterFromActivity:
    """Test the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant(self, reset_activities):
        """Should successfully unregister an existing participant"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]
    
    def test_unregister_removes_participant_from_activity(self, reset_activities):
        """Unregister should remove participant from the activity's list"""
        email = "michael@mergington.edu"
        client.delete(f"/activities/Chess%20Club/unregister?email={email}")
        
        response = client.get("/activities")
        activity = response.json()["Chess Club"]
        assert email not in activity["participants"]
    
    def test_unregister_nonexistent_participant_fails(self, reset_activities):
        """Unregistering a non-existent participant should fail"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_nonexistent_activity_fails(self, reset_activities):
        """Unregistering from non-existent activity should fail"""
        response = client.delete(
            "/activities/Nonexistent%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_decrements_participant_count(self, reset_activities):
        """Unregister should decrement the participant count"""
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
        
        response = client.get("/activities")
        new_count = len(response.json()["Chess Club"]["participants"])
        assert new_count == initial_count - 1


class TestWorkflow:
    """Test complete workflows"""
    
    def test_signup_and_unregister_workflow(self, reset_activities):
        """Test signing up and then unregistering"""
        email = "workflow@mergington.edu"
        activity = "Chess Club"
        
        # Sign up
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify signed up
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify unregistered
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
    
    def test_multiple_participants_same_activity(self, reset_activities):
        """Test multiple participants can sign up for the same activity"""
        activity = "Chess Club"
        participants = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        for email in participants:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        response = client.get("/activities")
        activity_data = response.json()[activity]
        for email in participants:
            assert email in activity_data["participants"]
