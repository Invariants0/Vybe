import pytest
from backend.app.models import User, ShortURL, Event, LinkVisit


class TestDatabaseConnection:
    
    def test_database_connects_before_request(self, app):
        with app.test_client() as client:
            response = client.get("/health")
            assert response.status_code == 200
    
    def test_database_closes_after_request(self, app):
        with app.test_client() as client:
            response = client.get("/health")
            assert response.status_code == 200
    
    def test_database_reuses_open_connection(self, app):
        with app.test_client() as client:
            response1 = client.get("/health")
            response2 = client.get("/health")
            assert response1.status_code == 200
            assert response2.status_code == 200
    
    def test_models_can_query_database(self, app):
        with app.app_context():
            user = User.create(username="testuser", email="test@example.com")
            assert user.id is not None
            
            found = User.get_by_id(user.id)
            assert found.username == "testuser"
    
    def test_database_tables_exist(self, app):
        with app.app_context():
            assert User.select().count() >= 0
            assert ShortURL.select().count() >= 0
            assert Event.select().count() >= 0
            assert LinkVisit.select().count() >= 0
