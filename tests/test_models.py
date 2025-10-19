"""
Test cases for data models and business logic validation.
"""

import pytest
from src.app import activities


class TestDataModels:
    """Test cases for data model structure and validation."""
    
    def test_activity_structure(self, reset_activities):
        """Test that all activities have the required structure."""
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str), f"Activity name should be string: {activity_name}"
            assert isinstance(activity_data, dict), f"Activity data should be dict: {activity_name}"
            
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in activity '{activity_name}'"
            
            # Test field types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            assert activity_data["max_participants"] > 0
            
            # Test participants are strings (emails)
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation
    
    def test_activity_capacity_constraints(self, reset_activities):
        """Test that no activity exceeds its capacity."""
        for activity_name, activity_data in activities.items():
            current_participants = len(activity_data["participants"])
            max_participants = activity_data["max_participants"]
            
            assert current_participants <= max_participants, (
                f"Activity '{activity_name}' has {current_participants} participants "
                f"but max is {max_participants}"
            )
    
    def test_participant_email_uniqueness_within_activity(self, reset_activities):
        """Test that each activity has unique participant emails."""
        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            unique_participants = set(participants)
            
            assert len(participants) == len(unique_participants), (
                f"Activity '{activity_name}' has duplicate participants"
            )
    
    def test_activity_names_are_unique(self, reset_activities):
        """Test that activity names are unique (should be guaranteed by dict structure)."""
        activity_names = list(activities.keys())
        unique_names = set(activity_names)
        
        assert len(activity_names) == len(unique_names)


class TestBusinessLogic:
    """Test business logic and constraints."""
    
    def test_spots_available_calculation(self, reset_activities):
        """Test calculation of available spots."""
        for activity_name, activity_data in activities.items():
            spots_left = activity_data["max_participants"] - len(activity_data["participants"])
            
            # Spots left should never be negative
            assert spots_left >= 0, f"Activity '{activity_name}' has negative spots available"
    
    def test_initial_activity_state(self, reset_activities):
        """Test the initial state of activities is valid."""
        # Test we have expected number of activities
        assert len(activities) == 9
        
        # Test specific activities exist
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", "Soccer Team",
            "Basketball Club", "Art Workshop", "Drama Club", "Math Olympiad", "Science Club"
        ]
        
        for expected_activity in expected_activities:
            assert expected_activity in activities
    
    def test_participant_email_format_basic(self, reset_activities):
        """Test basic email format validation for existing participants."""
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                # Basic checks
                assert "@" in participant, f"Invalid email format: {participant}"
                assert participant.endswith("@mergington.edu"), (
                    f"Email should end with @mergington.edu: {participant}"
                )
                assert len(participant) > len("@mergington.edu"), (
                    f"Email too short: {participant}"
                )


class TestActivityManipulation:
    """Test direct manipulation of activity data (simulating API operations)."""
    
    def test_add_participant_to_activity(self, reset_activities):
        """Test adding a participant to an activity."""
        activity_name = "Chess Club"
        new_participant = "newtest@mergington.edu"
        
        # Store initial state
        initial_count = len(activities[activity_name]["participants"])
        
        # Add participant
        activities[activity_name]["participants"].append(new_participant)
        
        # Verify addition
        assert len(activities[activity_name]["participants"]) == initial_count + 1
        assert new_participant in activities[activity_name]["participants"]
    
    def test_remove_participant_from_activity(self, reset_activities):
        """Test removing a participant from an activity."""
        activity_name = "Chess Club"
        participant_to_remove = "michael@mergington.edu"
        
        # Verify participant exists
        assert participant_to_remove in activities[activity_name]["participants"]
        
        # Store initial state
        initial_count = len(activities[activity_name]["participants"])
        
        # Remove participant
        activities[activity_name]["participants"].remove(participant_to_remove)
        
        # Verify removal
        assert len(activities[activity_name]["participants"]) == initial_count - 1
        assert participant_to_remove not in activities[activity_name]["participants"]
    
    def test_activity_capacity_enforcement(self, reset_activities):
        """Test that we can simulate capacity enforcement."""
        # Create a test scenario with a nearly full activity
        activity_name = "Math Olympiad"  # Has max 16, currently has 2
        activity = activities[activity_name]
        
        # Fill it up to capacity
        for i in range(activity["max_participants"] - len(activity["participants"])):
            activity["participants"].append(f"student{i}@mergington.edu")
        
        # Verify it's now full
        assert len(activity["participants"]) == activity["max_participants"]
        
        # Simulate capacity check
        is_full = len(activity["participants"]) >= activity["max_participants"]
        assert is_full == True


class TestDataIntegrity:
    """Test data integrity and consistency."""
    
    def test_activity_data_immutable_structure(self, reset_activities):
        """Test that the basic structure remains intact after operations."""
        original_keys = set(activities.keys())
        
        # Perform some operations
        activities["Chess Club"]["participants"].append("temp@mergington.edu")
        activities["Programming Class"]["participants"].remove("emma@mergington.edu")
        
        # Structure should remain the same
        assert set(activities.keys()) == original_keys
        
        # All activities should still have required fields
        required_fields = ["description", "schedule", "max_participants", "participants"]
        for activity_data in activities.values():
            for field in required_fields:
                assert field in activity_data
    
    def test_reset_activities_fixture(self, reset_activities):
        """Test that the reset_activities fixture works correctly."""
        # Modify the activities
        original_chess_participants = activities["Chess Club"]["participants"].copy()
        activities["Chess Club"]["participants"].append("fixture_test@mergington.edu")
        
        # Verify modification worked
        assert "fixture_test@mergington.edu" in activities["Chess Club"]["participants"]
        
        # The fixture should reset this after the test, which we can't test directly
        # but we can test that we have the expected initial state
        expected_chess_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # Reset manually to test the concept
        activities["Chess Club"]["participants"] = expected_chess_participants.copy()
        assert activities["Chess Club"]["participants"] == expected_chess_participants