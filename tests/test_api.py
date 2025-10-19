"""
Test cases for the High School Management System API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import activities


class TestRootEndpoint:
    """Test cases for the root endpoint."""
    
    def test_root_redirect(self, client):
        """Test that root redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary Redirect
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Test cases for the activities endpoint."""
    
    def test_get_activities_success(self, client, reset_activities):
        """Test successful retrieval of all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        
        # Check structure of an activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_contains_all_expected_activities(self, client, reset_activities):
        """Test that all expected activities are returned."""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Soccer Team",
            "Basketball Club", "Art Workshop", "Drama Club", "Math Olympiad", "Science Club"
        ]
        
        for activity in expected_activities:
            assert activity in data


class TestSignupEndpoint:
    """Test cases for the signup endpoint."""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful student signup."""
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        # Verify student is not already signed up
        initial_participants = activities[activity]["participants"].copy()
        assert email not in initial_participants
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity}"
        
        # Verify student was added to activity
        assert email in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == len(initial_participants) + 1
    
    def test_signup_duplicate_student(self, client, reset_activities):
        """Test signup fails for duplicate student."""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup fails for nonexistent activity."""
        email = "student@mergington.edu"
        activity = "Nonexistent Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_activity_full(self, client, reset_activities):
        """Test signup fails when activity is full."""
        # Create a small activity that we can fill up
        activities["Test Club"] = {
            "description": "Test activity",
            "schedule": "Test schedule",
            "max_participants": 2,
            "participants": ["student1@mergington.edu", "student2@mergington.edu"]
        }
        
        email = "newstudent@mergington.edu"
        response = client.post("/activities/Test%20Club/signup?email=" + email)
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Activity is full"
        
        # Clean up
        del activities["Test Club"]
    
    def test_signup_url_encoding(self, client, reset_activities):
        """Test signup with URL-encoded activity name."""
        email = "newstudent@mergington.edu"
        activity_encoded = "Programming%20Class"
        
        response = client.post(f"/activities/{activity_encoded}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify student was added
        assert email in activities["Programming Class"]["participants"]


class TestUnregisterEndpoint:
    """Test cases for the unregister endpoint."""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful student unregistration."""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        # Verify student is currently signed up
        initial_participants = activities[activity]["participants"].copy()
        assert email in initial_participants
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Unregistered {email} from {activity}"
        
        # Verify student was removed from activity
        assert email not in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == len(initial_participants) - 1
    
    def test_unregister_student_not_registered(self, client, reset_activities):
        """Test unregister fails for student not registered."""
        email = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student not registered for this activity"
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister fails for nonexistent activity."""
        email = "student@mergington.edu"
        activity = "Nonexistent Club"
        
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_url_encoding(self, client, reset_activities):
        """Test unregister with URL-encoded activity name."""
        email = "emma@mergington.edu"  # Already in Programming Class
        activity_encoded = "Programming%20Class"
        
        response = client.delete(f"/activities/{activity_encoded}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify student was removed
        assert email not in activities["Programming Class"]["participants"]


class TestEndToEndWorkflows:
    """Test complete workflows combining multiple endpoints."""
    
    def test_signup_and_unregister_workflow(self, client, reset_activities):
        """Test complete signup and unregister workflow."""
        email = "workflow@mergington.edu"
        activity = "Chess Club"
        
        # 1. Get initial activities
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_participants = len(initial_data[activity]["participants"])
        
        # 2. Sign up student
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # 3. Verify signup in activities list
        after_signup = client.get("/activities")
        after_signup_data = after_signup.json()
        assert len(after_signup_data[activity]["participants"]) == initial_participants + 1
        assert email in after_signup_data[activity]["participants"]
        
        # 4. Unregister student
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # 5. Verify unregistration in activities list
        after_unregister = client.get("/activities")
        after_unregister_data = after_unregister.json()
        assert len(after_unregister_data[activity]["participants"]) == initial_participants
        assert email not in after_unregister_data[activity]["participants"]
    
    def test_multiple_signups_same_student(self, client, reset_activities):
        """Test student can sign up for multiple different activities."""
        email = "multisport@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Art Workshop"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify student is in all activities
        final_activities = client.get("/activities").json()
        for activity in activities_to_join:
            assert email in final_activities[activity]["participants"]
    
    def test_activity_capacity_management(self, client, reset_activities):
        """Test that activity capacity is properly managed."""
        # Create a test activity with limited capacity
        activities["Limited Club"] = {
            "description": "Test limited capacity",
            "schedule": "Test schedule",
            "max_participants": 3,
            "participants": ["existing@mergington.edu"]
        }
        
        # Fill up the remaining spots
        emails = ["student1@mergington.edu", "student2@mergington.edu"]
        for email in emails:
            response = client.post("/activities/Limited%20Club/signup?email=" + email)
            assert response.status_code == 200
        
        # Try to add one more (should fail)
        overflow_response = client.post("/activities/Limited%20Club/signup?email=overflow@mergington.edu")
        assert overflow_response.status_code == 400
        assert overflow_response.json()["detail"] == "Activity is full"
        
        # Unregister one student
        unregister_response = client.delete("/activities/Limited%20Club/unregister?email=student1@mergington.edu")
        assert unregister_response.status_code == 200
        
        # Now we should be able to add the overflow student
        retry_response = client.post("/activities/Limited%20Club/signup?email=overflow@mergington.edu")
        assert retry_response.status_code == 200
        
        # Clean up
        del activities["Limited Club"]


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_email_formats(self, client, reset_activities):
        """Test various email formats (API should accept them as strings)."""
        activity = "Chess Club"
        test_emails = [
            "valid@mergington.edu",
            "also.valid+tag@mergington.edu",
            "edge-case@sub.mergington.edu",
            "numbers123@mergington.edu"
        ]
        
        for email in test_emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
            
            # Clean up for next iteration
            client.delete(f"/activities/{activity}/unregister?email={email}")
    
    def test_empty_parameters(self, client, reset_activities):
        """Test handling of empty parameters."""
        # Empty email
        response = client.post("/activities/Chess%20Club/signup?email=")
        # API should still work (it's just treating empty string as email)
        assert response.status_code in [200, 400]  # Depends on validation
        
        # Empty activity name would be a 404 due to routing
        response = client.post("/activities//signup?email=test@mergington.edu")
        assert response.status_code == 404
    
    def test_special_characters_in_activity_names(self, client, reset_activities):
        """Test handling of special characters in activity names."""
        # Add a test activity with special characters
        activities["Test & Fun Club"] = {
            "description": "Test activity with special chars",
            "schedule": "Test schedule",
            "max_participants": 10,
            "participants": []
        }
        
        email = "special@mergington.edu"
        encoded_activity = "Test%20%26%20Fun%20Club"
        
        response = client.post(f"/activities/{encoded_activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Clean up
        del activities["Test & Fun Club"]