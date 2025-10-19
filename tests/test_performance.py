"""
Performance and load tests for the High School Management System API.
"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.app import activities


class TestPerformance:
    """Test performance characteristics of the API."""
    
    def test_get_activities_response_time(self, client, reset_activities):
        """Test that getting activities responds quickly."""
        start_time = time.time()
        response = client.get("/activities")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # Should respond within 1 second (very generous for this simple API)
        assert response_time < 1.0, f"Response time too slow: {response_time:.3f}s"
    
    def test_signup_response_time(self, client, reset_activities):
        """Test that signup operations are fast."""
        email = "performance@mergington.edu"
        activity = "Chess Club"
        
        start_time = time.time()
        response = client.post(f"/activities/{activity}/signup?email={email}")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # Should respond within 1 second
        assert response_time < 1.0, f"Signup response time too slow: {response_time:.3f}s"
    
    def test_multiple_concurrent_signups(self, client, reset_activities):
        """Test handling of concurrent signup requests."""
        base_email = "concurrent"
        activity = "Programming Class"  # Has more capacity
        num_concurrent = 5
        
        def signup_student(index):
            email = f"{base_email}{index}@mergington.edu"
            return client.post(f"/activities/{activity}/signup?email={email}")
        
        # Execute concurrent signups
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(signup_student, i) for i in range(num_concurrent)]
            results = [future.result() for future in as_completed(futures)]
        
        # All should succeed (assuming capacity allows)
        success_count = sum(1 for result in results if result.status_code == 200)
        assert success_count == num_concurrent, f"Only {success_count}/{num_concurrent} signups succeeded"
        
        # Verify all students were actually added
        final_activities = client.get("/activities").json()
        for i in range(num_concurrent):
            email = f"{base_email}{i}@mergington.edu"
            assert email in final_activities[activity]["participants"]
    
    def test_large_activity_list_performance(self, client, reset_activities):
        """Test performance with a larger number of activities."""
        # Add many test activities
        num_test_activities = 50
        
        for i in range(num_test_activities):
            activities[f"Test Activity {i}"] = {
                "description": f"Test activity number {i}",
                "schedule": f"Day {i % 7}, {i % 12 + 1}:00 PM",
                "max_participants": 20,
                "participants": [f"student{j}@mergington.edu" for j in range(i % 5)]
            }
        
        start_time = time.time()
        response = client.get("/activities")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        data = response.json()
        
        # Should still respond quickly even with many activities
        assert response_time < 2.0, f"Response time with large dataset too slow: {response_time:.3f}s"
        assert len(data) >= num_test_activities + 9  # Original activities plus test ones
        
        # Clean up
        for i in range(num_test_activities):
            del activities[f"Test Activity {i}"]


class TestStressConditions:
    """Test API behavior under stress conditions."""
    
    def test_activity_at_capacity_stress(self, client, reset_activities):
        """Test behavior when activity reaches capacity under load."""
        # Create a small capacity activity
        activities["Stress Test Club"] = {
            "description": "Small capacity for stress testing",
            "schedule": "Test schedule",
            "max_participants": 3,
            "participants": []
        }
        
        # Try to add more students than capacity allows
        num_attempts = 10
        successful_signups = 0
        capacity_errors = 0
        
        for i in range(num_attempts):
            email = f"stress{i}@mergington.edu"
            response = client.post("/activities/Stress%20Test%20Club/signup?email=" + email)
            
            if response.status_code == 200:
                successful_signups += 1
            elif response.status_code == 400 and "full" in response.json().get("detail", ""):
                capacity_errors += 1
        
        # Should have exactly max_participants successful signups
        assert successful_signups == 3
        assert capacity_errors == 7  # Remaining attempts should fail
        assert successful_signups + capacity_errors == num_attempts
        
        # Clean up
        del activities["Stress Test Club"]
    
    def test_rapid_signup_unregister_cycles(self, client, reset_activities):
        """Test rapid cycles of signup and unregister."""
        email = "cycle@mergington.edu"
        activity = "Art Workshop"
        cycles = 10
        
        for cycle in range(cycles):
            # Sign up
            signup_response = client.post(f"/activities/{activity}/signup?email={email}")
            assert signup_response.status_code == 200, f"Signup failed on cycle {cycle}"
            
            # Verify signup
            activities_response = client.get("/activities")
            activities_data = activities_response.json()
            assert email in activities_data[activity]["participants"], f"Student not found after signup on cycle {cycle}"
            
            # Unregister
            unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
            assert unregister_response.status_code == 200, f"Unregister failed on cycle {cycle}"
            
            # Verify unregister
            activities_response = client.get("/activities")
            activities_data = activities_response.json()
            assert email not in activities_data[activity]["participants"], f"Student still found after unregister on cycle {cycle}"


class TestResourceUsage:
    """Test resource usage patterns."""
    
    def test_memory_usage_stability(self, client, reset_activities):
        """Test that repeated operations don't cause memory leaks."""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform many operations
        for i in range(100):
            # Get activities
            client.get("/activities")
            
            # Sign up and unregister
            email = f"memory_test{i % 10}@mergington.edu"
            activity = list(activities.keys())[i % len(activities)]
            
            # Only signup if not already registered
            activities_data = client.get("/activities").json()
            if email not in activities_data[activity]["participants"]:
                client.post(f"/activities/{activity}/signup?email={email}")
            
            # Unregister
            client.delete(f"/activities/{activity}/unregister?email={email}")
        
        # Check final memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 10MB for this simple API)
        max_acceptable_increase = 10 * 1024 * 1024  # 10MB in bytes
        assert memory_increase < max_acceptable_increase, (
            f"Memory usage increased too much: {memory_increase / (1024*1024):.2f}MB"
        )
    
    @pytest.mark.slow
    def test_sustained_load(self, client, reset_activities):
        """Test API under sustained load (marked as slow test)."""
        duration_seconds = 5
        start_time = time.time()
        request_count = 0
        errors = 0
        
        while time.time() - start_time < duration_seconds:
            try:
                response = client.get("/activities")
                request_count += 1
                if response.status_code != 200:
                    errors += 1
            except Exception:
                errors += 1
            
            # Small delay to prevent overwhelming
            time.sleep(0.01)
        
        requests_per_second = request_count / duration_seconds
        error_rate = errors / request_count if request_count > 0 else 1
        
        # Should handle at least 10 requests per second with low error rate
        assert requests_per_second > 10, f"Too few requests per second: {requests_per_second:.2f}"
        assert error_rate < 0.01, f"Error rate too high: {error_rate:.2%}"