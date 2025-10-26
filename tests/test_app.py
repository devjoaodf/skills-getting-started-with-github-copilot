import pytest
from fastapi.testclient import TestClient
from src.app import app

# Create a test client
client = TestClient(app)

def test_root_redirect():
    """Test that the root endpoint redirects to index.html"""
    response = client.get("/")
    assert response.status_code == 200 or response.status_code == 307
    
def test_get_activities():
    """Test retrieving all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Check that each activity has the required fields
    for activity in activities.values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

def test_signup_for_activity():
    """Test signing up for an activity"""
    # Test with valid data
    email = "test@mergington.edu"
    activity_name = "Chess Club"  # Using a known activity
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify the student was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]
    
def test_signup_for_nonexistent_activity():
    """Test signing up for an activity that doesn't exist"""
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_unregister_from_activity():
    """Test unregistering from an activity"""
    # First, sign up a test user
    email = "unregister_test@mergington.edu"
    activity_name = "Chess Club"
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Now test unregistering
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert "message" in response.json()
    
    # Verify the student was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_from_nonexistent_activity():
    """Test unregistering from an activity that doesn't exist"""
    response = client.delete("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "detail" in response.json()

def test_unregister_nonexistent_participant():
    """Test unregistering a participant that isn't registered"""
    response = client.delete("/activities/Chess Club/unregister?email=notregistered@mergington.edu")
    assert response.status_code == 400
    assert "detail" in response.json()