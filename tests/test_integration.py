"""Integration tests for database operations and API endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import User, Calculation

# Create test database
import os
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create and drop database tables for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestUserEndpoints:
    """Test suite for user endpoints."""
    
    def test_register_user(self):
        """Test successful user registration."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123"
        }
        response = client.post("/users/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data
        
    def test_register_duplicate_email(self):
        """Test registration with duplicate email."""
        user_data = {
            "username": "testuser1",
            "email": "test@example.com",
            "password": "securepass123"
        }
        client.post("/users/register", json=user_data)
        
        user_data2 = {
            "username": "testuser2",
            "email": "test@example.com",
            "password": "securepass123"
        }
        response = client.post("/users/register", json=user_data2)
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_login_success(self):
        """Test successful login."""
        # Register first
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123"
        }
        client.post("/users/register", json=user_data)
        
        # Login
        login_data = {
            "username": "testuser",
            "password": "securepass123"
        }
        response = client.post("/users/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
    def test_login_failure(self):
        """Test login with wrong password."""
        # Register first
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123"
        }
        client.post("/users/register", json=user_data)
        
        # Login with wrong password
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = client.post("/users/login", json=login_data)
        assert response.status_code == 401


class TestCalculationEndpoints:
    """Test suite for calculation endpoints."""
    
    def test_create_calculation(self):
        """Test creating a calculation."""
        calc_data = {
            "a": 10,
            "b": 5,
            "type": "Add"
        }
        response = client.post("/calculations/", json=calc_data)
        assert response.status_code == 201
        data = response.json()
        assert data["result"] == 15
        assert data["type"] == "Add"
        
    def test_create_calculation_with_user(self):
        """Test creating a calculation linked to a user."""
        # Register user
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123"
        }
        user_res = client.post("/users/register", json=user_data)
        user_id = user_res.json()["id"]
        
        calc_data = {
            "a": 10,
            "b": 5,
            "type": "Multiply",
            "user_id": user_id
        }
        response = client.post("/calculations/", json=calc_data)
        assert response.status_code == 201
        data = response.json()
        assert data["result"] == 50
        assert data["user_id"] == user_id

    def test_read_calculations(self):
        """Test reading all calculations."""
        client.post("/calculations/", json={"a": 1, "b": 1, "type": "Add"})
        client.post("/calculations/", json={"a": 2, "b": 2, "type": "Add"})
        
        response = client.get("/calculations/")
        assert response.status_code == 200
        assert len(response.json()) == 2
        
    def test_read_calculation_by_id(self):
        """Test reading a specific calculation."""
        res = client.post("/calculations/", json={"a": 10, "b": 2, "type": "Divide"})
        calc_id = res.json()["id"]
        
        response = client.get(f"/calculations/{calc_id}")
        assert response.status_code == 200
        assert response.json()["result"] == 5
        
    def test_update_calculation(self):
        """Test updating a calculation."""
        res = client.post("/calculations/", json={"a": 10, "b": 5, "type": "Add"})
        calc_id = res.json()["id"]
        
        # Update to Subtract
        update_data = {
            "type": "Subtract"
        }
        response = client.put(f"/calculations/{calc_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "Subtract"
        assert data["result"] == 5  # 10 - 5
        
    def test_delete_calculation(self):
        """Test deleting a calculation."""
        res = client.post("/calculations/", json={"a": 10, "b": 5, "type": "Add"})
        calc_id = res.json()["id"]
        
        response = client.delete(f"/calculations/{calc_id}")
        assert response.status_code == 204
        
        # Verify deletion
        get_res = client.get(f"/calculations/{calc_id}")
        assert get_res.status_code == 404

    def test_divide_by_zero(self):
        """Test division by zero error."""
        calc_data = {
            "a": 10,
            "b": 0,
            "type": "Divide"
        }
        response = client.post("/calculations/", json=calc_data)
        assert response.status_code == 422
