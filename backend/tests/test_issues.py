import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.conftest import client, test_user, test_admin_user, test_issue

def get_auth_headers(client, email, password):
    """Helper function to get authentication headers"""
    login_data = {"username": email, "password": password}
    response = client.post("/token", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_issue(client, test_user):
    """Test creating an issue"""
    headers = get_auth_headers(client, "test@example.com", "testpassword")
    issue_data = {
        "title": "New Test Issue",
        "description": "This is a test issue",
        "severity": "HIGH"
    }
    response = client.post("/issues/", json=issue_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == issue_data["title"]
    assert data["description"] == issue_data["description"]
    assert data["severity"] == issue_data["severity"]
    assert data["status"] == "OPEN"

def test_get_issues(client, test_user, test_issue):
    """Test getting issues list"""
    headers = get_auth_headers(client, "test@example.com", "testpassword")
    response = client.get("/issues/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_get_issue(client, test_user, test_issue):
    """Test getting a specific issue"""
    headers = get_auth_headers(client, "test@example.com", "testpassword")
    response = client.get(f"/issues/{test_issue.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_issue.id
    assert data["title"] == test_issue.title

def test_update_issue_admin(client, test_admin_user, test_issue):
    """Test updating an issue as admin"""
    headers = get_auth_headers(client, "admin@example.com", "adminpassword")
    update_data = {
        "status": "IN_PROGRESS",
        "title": "Updated Issue Title"
    }
    response = client.put(f"/issues/{test_issue.id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == update_data["status"]
    assert data["title"] == update_data["title"]

def test_update_issue_reporter_denied(client, test_user, test_issue):
    """Test that reporter cannot update issue status"""
    headers = get_auth_headers(client, "test@example.com", "testpassword")
    update_data = {"status": "IN_PROGRESS"}
    response = client.put(f"/issues/{test_issue.id}", json=update_data, headers=headers)
    assert response.status_code == 403

def test_delete_issue_admin(client, test_admin_user, test_issue):
    """Test deleting an issue as admin"""
    headers = get_auth_headers(client, "admin@example.com", "adminpassword")
    response = client.delete(f"/issues/{test_issue.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["ok"] == True

def test_delete_issue_reporter_denied(client, test_user, test_issue):
    """Test that reporter cannot delete issues"""
    headers = get_auth_headers(client, "test@example.com", "testpassword")
    response = client.delete(f"/issues/{test_issue.id}", headers=headers)
    assert response.status_code == 403

def test_get_nonexistent_issue(client, test_user):
    """Test getting a non-existent issue"""
    headers = get_auth_headers(client, "test@example.com", "testpassword")
    response = client.get("/issues/999", headers=headers)
    assert response.status_code == 404

def test_create_issue_unauthorized(client):
    """Test creating issue without authentication"""
    issue_data = {
        "title": "Unauthorized Issue",
        "description": "This should fail",
        "severity": "LOW"
    }
    response = client.post("/issues/", json=issue_data)
    assert response.status_code == 401 