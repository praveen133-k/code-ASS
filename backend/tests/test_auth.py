import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import client, test_user

def test_create_user(client):
    """Test user registration"""
    user_data = {
        "email": "newuser@example.com",
        "password": "newpassword",
        "role": "REPORTER"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["role"] == user_data["role"]
    assert "id" in data

def test_create_user_duplicate_email(client, test_user):
    """Test user registration with duplicate email"""
    user_data = {
        "email": "test@example.com",
        "password": "password",
        "role": "REPORTER"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_login_success(client, test_user):
    """Test successful login"""
    login_data = {
        "username": "test@example.com",
        "password": "testpassword"
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_get_current_user(client, test_user):
    """Test getting current user with valid token"""
    # First login to get token
    login_data = {
        "username": "test@example.com",
        "password": "testpassword"
    }
    login_response = client.post("/token", data=login_data)
    token = login_response.json()["access_token"]
    
    # Use token to get current user
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["role"] == test_user.role

def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/users/me/", headers=headers)
    assert response.status_code == 401 