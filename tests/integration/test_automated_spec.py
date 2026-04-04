"""
Integration tests matching AUTOMATED_TESTS.md specification.
These tests verify compliance with MLH Production Engineering Hackathon requirements.
"""
import io
import pytest


class TestHealth:
    """Test Category 1: Health endpoint"""
    
    def test_health_endpoint(self, client):
        """Ensure the API is running and ready to accept requests."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert "status" in data
        assert data["status"] == "ok"


class TestUsers:
    """Test Category 2: User endpoints"""
    
    def test_bulk_load_users_csv(self, client):
        """2.1 Bulk Load Users (CSV Import)"""
        # Create a CSV file in memory with the format expected by the service
        csv_content = b"id,username,email,created_at\n1,silvertrail15,silvertrail15@hackstack.io,2025-09-19 22:25:05\n2,urbancanyon36,urbancanyon36@opswise.net,2024-04-09 02:51:03"
        
        data = {
            'file': (io.BytesIO(csv_content), 'users.csv')
        }
        
        response = client.post(
            "/users/bulk",
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code in [200, 201]
        result = response.get_json()
        
        # Accept multiple response formats
        if "count" in result:
            assert result["count"] == 2
        elif "imported" in result:
            assert result["imported"] == 2
        elif isinstance(result, list):
            assert len(result) == 2
    
    def test_list_users(self, client):
        """2.2 List Users"""
        # Create test users
        client.post("/users", json={"username": "silvertrail15", "email": "silvertrail15@hackstack.io"})
        client.post("/users", json={"username": "urbancanyon36", "email": "urbancanyon36@opswise.net"})
        
        response = client.get("/users")
        assert response.status_code == 200
        
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 2
        
        # Verify structure of user objects
        user = data[0]
        assert "id" in user
        assert "username" in user
        assert "email" in user
        assert "created_at" in user
    
    def test_get_user_by_id(self, client):
        """2.3 Get User by ID"""
        # Create a user
        create_response = client.post("/users", json={
            "username": "silvertrail15",
            "email": "silvertrail15@hackstack.io"
        })
        user_id = create_response.get_json()["id"]
        
        # Get user by ID
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200
        
        data = response.get_json()
        assert data["id"] == user_id
        assert data["username"] == "silvertrail15"
        assert data["email"] == "silvertrail15@hackstack.io"
        assert "created_at" in data
    
    def test_create_user(self, client):
        """2.4 Create User"""
        response = client.post("/users", json={
            "username": "testuser",
            "email": "testuser@example.com"
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert "id" in data
        assert data["username"] == "testuser"
        assert data["email"] == "testuser@example.com"
        assert "created_at" in data
    
    def test_create_user_invalid_schema(self, client):
        """2.4 Create User - Error Handling"""
        # Test with integer for username (type mismatch)
        response = client.post("/users", json={
            "username": 12345,
            "email": "test@example.com"
        })
        
        assert response.status_code in [400, 422]
        data = response.get_json()
        assert "error" in data
    
    def test_create_user_invalid_email(self, client):
        """2.4 Create User - Invalid email format"""
        response = client.post("/users", json={
            "username": "testuser",
            "email": "invalid-email"
        })
        
        assert response.status_code in [400, 422]
        data = response.get_json()
        assert "error" in data
    
    def test_update_user(self, client):
        """2.5 Update User"""
        # Create a user
        create_response = client.post("/users", json={
            "username": "silvertrail15",
            "email": "silvertrail15@hackstack.io"
        })
        user_id = create_response.get_json()["id"]
        
        # Update username
        response = client.put(f"/users/{user_id}", json={
            "username": "updated_username"
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data["id"] == user_id
        assert data["username"] == "updated_username"
        assert data["email"] == "silvertrail15@hackstack.io"  # Email unchanged
        assert "created_at" in data


class TestURLs:
    """Test Category 3: URL endpoints"""
    
    def test_create_url(self, client):
        """3.1 Create URL"""
        # Create a user first
        user_response = client.post("/users", json={
            "username": "testuser",
            "email": "test@example.com"
        })
        user_id = user_response.get_json()["id"]
        
        # Create URL
        response = client.post("/urls", json={
            "user_id": user_id,
            "original_url": "https://example.com/test",
            "title": "Test URL"
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert "id" in data
        assert data["user_id"] == user_id
        assert "short_code" in data
        assert data["original_url"] == "https://example.com/test"
        assert data["title"] == "Test URL"
        assert data["is_active"] is True
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_url_missing_user(self, client):
        """3.1 Create URL - Error Handling for missing user"""
        response = client.post("/urls", json={
            "user_id": 999999,
            "original_url": "https://example.com/test",
            "title": "Test URL"
        })
        
        # Should handle missing user gracefully
        assert response.status_code in [400, 404, 422]
    
    def test_list_urls(self, client):
        """3.2 List URLs"""
        # Create user and URL
        user_response = client.post("/users", json={
            "username": "testuser",
            "email": "test@example.com"
        })
        user_id = user_response.get_json()["id"]
        
        client.post("/urls", json={
            "user_id": user_id,
            "original_url": "https://opswise.net/harbor/journey/1",
            "title": "Service guide lagoon"
        })
        
        # List all URLs
        response = client.get("/urls")
        assert response.status_code == 200
        
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verify structure
        url = data[0]
        assert "id" in url
        assert "user_id" in url
        assert "short_code" in url
        assert "original_url" in url
        assert "title" in url
        assert "is_active" in url
        assert "created_at" in url
        assert "updated_at" in url
    
    def test_list_urls_filter_by_user(self, client):
        """3.2 List URLs - Filter by user_id"""
        # Create two users
        user1_response = client.post("/users", json={
            "username": "user1",
            "email": "user1@example.com"
        })
        user1_id = user1_response.get_json()["id"]
        
        user2_response = client.post("/users", json={
            "username": "user2",
            "email": "user2@example.com"
        })
        user2_id = user2_response.get_json()["id"]
        
        # Create URLs for each user
        client.post("/urls", json={
            "user_id": user1_id,
            "original_url": "https://example.com/user1"
        })
        client.post("/urls", json={
            "user_id": user2_id,
            "original_url": "https://example.com/user2"
        })
        
        # Filter by user1
        response = client.get(f"/urls?user_id={user1_id}")
        assert response.status_code == 200
        
        data = response.get_json()
        # All returned URLs should belong to user1
        for url in data:
            assert url["user_id"] == user1_id
    
    def test_get_url_by_id(self, client):
        """3.3 Get URL by ID"""
        # Create user and URL
        user_response = client.post("/users", json={
            "username": "testuser",
            "email": "test@example.com"
        })
        user_id = user_response.get_json()["id"]
        
        url_response = client.post("/urls", json={
            "user_id": user_id,
            "original_url": "https://opswise.net/harbor/journey/1",
            "title": "Service guide lagoon"
        })
        url_id = url_response.get_json()["id"]
        
        # Get URL by ID
        response = client.get(f"/urls/{url_id}")
        assert response.status_code == 200
        
        data = response.get_json()
        assert data["id"] == url_id
        assert data["user_id"] == user_id
        assert "short_code" in data
        assert data["original_url"] == "https://opswise.net/harbor/journey/1"
        assert data["title"] == "Service guide lagoon"
        assert data["is_active"] is True
    
    def test_update_url_details(self, client):
        """3.4 Update URL Details"""
        # Create user and URL
        user_response = client.post("/users", json={
            "username": "testuser",
            "email": "test@example.com"
        })
        user_id = user_response.get_json()["id"]
        
        url_response = client.post("/urls", json={
            "user_id": user_id,
            "original_url": "https://opswise.net/harbor/journey/1",
            "title": "Service guide lagoon"
        })
        url_id = url_response.get_json()["id"]
        
        # Update URL
        response = client.put(f"/urls/{url_id}", json={
            "title": "Updated Title",
            "is_active": False
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data["id"] == url_id
        assert data["title"] == "Updated Title"
        assert data["is_active"] is False
        assert data["original_url"] == "https://opswise.net/harbor/journey/1"  # Unchanged


class TestEvents:
    """Test Category 4: Events / Analytics"""
    
    def test_list_events(self, client):
        """4.1 List Events"""
        # Create user and URL to generate events
        user_response = client.post("/users", json={
            "username": "testuser",
            "email": "test@example.com"
        })
        user_id = user_response.get_json()["id"]
        
        url_response = client.post("/urls", json={
            "user_id": user_id,
            "original_url": "https://opswise.net/harbor/journey/1",
            "title": "Service guide lagoon"
        })
        url_id = url_response.get_json()["id"]
        
        # Get events
        response = client.get("/events")
        assert response.status_code == 200
        
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Find the created event
        created_events = [e for e in data if e.get("event_type") == "created"]
        assert len(created_events) >= 1
        
        # Verify event structure
        event = created_events[0]
        assert "id" in event
        # Accept both url_id and short_url_id field names
        assert "url_id" in event or "short_url_id" in event
        assert "user_id" in event
        assert "event_type" in event
        assert "timestamp" in event
        assert "details" in event or "metadata" in event


class TestEdgeCases:
    """Additional edge case tests"""
    
    def test_user_not_found(self, client):
        """Test 404 for non-existent user"""
        response = client.get("/users/999999")
        assert response.status_code == 404
    
    def test_url_not_found(self, client):
        """Test 404 for non-existent URL"""
        response = client.get("/urls/999999")
        assert response.status_code == 404
    
    def test_invalid_url_format(self, client):
        """Test URL validation"""
        user_response = client.post("/users", json={
            "username": "testuser",
            "email": "test@example.com"
        })
        user_id = user_response.get_json()["id"]
        
        response = client.post("/urls", json={
            "user_id": user_id,
            "original_url": "not-a-valid-url"
        })
        
        assert response.status_code in [400, 422]
    
    def test_missing_required_fields(self, client):
        """Test validation for missing required fields"""
        # Missing email
        response = client.post("/users", json={
            "username": "testuser"
        })
        assert response.status_code in [400, 422]
        
        # Missing username
        response = client.post("/users", json={
            "email": "test@example.com"
        })
        assert response.status_code in [400, 422]
